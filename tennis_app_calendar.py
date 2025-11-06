#!/usr/bin/env python3
"""Main Streamlit app moved here to avoid naming collision with the streamlit package.
Run this via: streamlit run streamlit.py  (streamlit.py is a small shim)
"""
import sys
import importlib
import os as _os
# Import the real `streamlit` package even if a local file named
# `streamlit.py` exists in the project directory by temporarily
# removing the project directory from sys.path while importing.
_THIS_DIR = _os.path.dirname(__file__)
if _THIS_DIR in sys.path:
    sys.path.remove(_THIS_DIR)
_streamlit_pkg = importlib.import_module("streamlit")
# restore path
sys.path.insert(0, _THIS_DIR)
st = _streamlit_pkg
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import os
import uuid
import re

# ---------- 設定 ----------
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "entries.csv")
TIME_REGEX = r"^([01]\d|2[0-3]):([0-5]\d)$"  # HH:MM
st.set_page_config(page_title="テニスコート予約管理（カレンダー）", page_icon="🎾", layout="centered")

# カラー（状態）
STATUS_COLORS = {
    "確保": "#7ED957",
    "抽選中": "#FFD66B",
    "中止": "#D9D9D9"
}

# ---------- ユーティリティ ----------
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["id","facility","date","start_time","end_time","nick","status","created_at"])
        df.to_csv(DATA_FILE, index=False)

def load_entries():
    ensure_data_dir()
    return pd.read_csv(DATA_FILE, parse_dates=["date","created_at"], dtype=str)

def save_entries(df):
    ensure_data_dir()
    df.to_csv(DATA_FILE, index=False)

def to_date(d):
    if isinstance(d, str):
        return pd.to_datetime(d).date()
    if isinstance(d, pd.Timestamp):
        return d.date()
    if isinstance(d, date):
        return d
    return None

def safe_parse_date_series(s):
    """安全に日付をパースして datetime.date を返すシリーズを返す。
    - 数字のみの文字列は桁数に応じて秒/ms/us/ns を順に試す
    - ISO 文字列や他の表記は pandas の to_datetime にフォールバック
    - 成功しなければ NaT にする
    """
    def parse_one(x):
        if pd.isna(x):
            return pd.NaT
        # accept datetime/date/Timestamp directly
        if isinstance(x, (pd.Timestamp, datetime)):
            return pd.Timestamp(x)
        if isinstance(x, date):
            return pd.Timestamp(x)
        s = str(x).strip()
        if s == "":
            return pd.NaT
        # numeric epoch-like
        if re.fullmatch(r"\d+", s):
            try:
                iv = int(s)
            except Exception:
                return pd.NaT
            # try units in order that commonly succeed for large ints
            for unit in ("ns", "us", "ms", "s"):
                try:
                    t = pd.to_datetime(iv, unit=unit, errors="coerce")
                except (OverflowError, ValueError):
                    t = pd.NaT
                if not pd.isna(t):
                    # sanity: year between 1970 and 2100
                    try:
                        y = int(t.year)
                    except Exception:
                        y = None
                    if y and 1970 <= y <= 2100:
                        return t
            return pd.NaT
        # fallback to pandas parser
        try:
            t = pd.to_datetime(s, errors="coerce")
            return t
        except Exception:
            return pd.NaT

    parsed = [parse_one(v) for v in s]
    # ensure we have a Series so .dt is available
    parsed = pd.to_datetime(pd.Series(parsed), errors="coerce")
    # return series of python date objects where possible
    return parsed.dt.date

def valid_time_str(t):
    if not isinstance(t, str): return False
    m = re.match(TIME_REGEX, t.strip())
    if not m: return False
    hh, mm = int(m.group(1)), int(m.group(2))
    return (mm % 10) == 0

def overlaps(existing_df, target_date, start, end, exclude_id=None):
    """同じ施設で時間帯重複チェック（単純判定）"""
    ed = existing_df.copy()
    # safe parse to avoid OutOfBoundsDatetime for malformed/epoch values
    ed["date"] = safe_parse_date_series(ed["date"]) 
    ed = ed[ed["date"] == target_date]
    if exclude_id:
        ed = ed[ed["id"] != exclude_id]
    for _, r in ed.iterrows():
        s = r["start_time"]
        e = r["end_time"]
        if s == "" or e == "": continue
        if not valid_time_str(s) or not valid_time_str(e): continue
        if not (end <= s or start >= e):
            return True
    return False

# ---------- セッション初期化 ----------
if "refresh" not in st.session_state:
    st.session_state.refresh = 0

# ---------- レイアウトCSS ----------
st.markdown("""
<style>
:root{--mint:#A8E6CF; --orange:#FFB997; --card:#F8FFF3; --muted:#6b6b6b;}
body { background-color: #ffffff; }
.header { display:flex; align-items:center; justify-content:space-between; }
.app-title { font-size:22px; font-weight:700; color:#116466; }
.sub { color:var(--muted); font-size:13px; }
/* Google カレンダー風 月表示 */
.calendar-grid { border: 1px solid #e0e0e0; margin-top: 1rem; display:block; }
.weekday-row { display:flex; }
.weekday-header { flex:1; padding:10px; text-align:center; font-weight:700; background:#fafafa; border-bottom:1px solid #e6e6e6; }
.month-body { display:block; }
.week-row { display:flex; }
.day-cell { 
    padding: 6px 8px; 
    background: #fff; 
    border-right: 1px solid #e9e9e9;
    border-bottom: 1px solid #e9e9e9;
    min-height: 140px;
    flex: 1 0 0;
    position: relative;
    display:flex;
    flex-direction:column;
}
.day-cell:last-child { border-right: none; }
.other-month { color: #bfbfbf; background:#fbfbfb; }
.day-number { position:absolute; top:6px; left:6px; width:28px; height:28px; line-height:28px; text-align:center; border-radius:50%; font-weight:700; color:#333; }
.today .day-number { background:#116466; color:#fff; }
.day-header { padding-left:44px; padding-top:4px; }
.day-events { margin-top:8px; overflow-y:auto; flex:1 1 auto; padding-right:4px; }
.event-pill { display:block; padding:6px 8px; border-radius:6px; margin:6px 4px; font-size:12px; color:#111; }
.event-time { font-weight:700; font-size:12px; }
.event-meta { font-size:11px; color:#333; }
.event-status { font-size:11px; opacity:0.95; }
.event-more { color:#666; font-size:12px; padding:4px 8px; }
/* button styling */
.date-btn { background:none; border:none; cursor:pointer; font-size:14px; }
@media (max-width:900px){
  .day-cell { min-height:110px; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="header"><div><div class="app-title">🎾 テニスコート予約管理</div><div class="sub">月表示カレンダー — タップで詳細・編集</div></div></div>', unsafe_allow_html=True)
st.markdown("---")

# ---------- カレンダー制御 ----------
today = date.today()
if "year_month" not in st.session_state:
    st.session_state.year_month = (today.year, today.month)

col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("◀ 前月"):
        y,m = st.session_state.year_month
        prev = (date(y,m,15) - timedelta(days=31))
        st.session_state.year_month = (prev.year, prev.month)
        st.session_state.refresh += 1
with col2:
    y,m = st.session_state.year_month
    st.markdown(f"### {y}年 {m}月", unsafe_allow_html=True)
with col3:
    if st.button("次月 ▶"):
        y,m = st.session_state.year_month
        nxt = (date(y,m,15) + timedelta(days=31))
        st.session_state.year_month = (nxt.year, nxt.month)
        st.session_state.refresh += 1

# load entries
df = load_entries()

# filters
with st.expander("🔎 フィルタ（施設・担当で絞る）", expanded=False):
    f_facility = st.text_input("施設名（部分一致）", value="")
    f_nick = st.text_input("担当ニックネーム（部分一致）", value="")
    show_legend = st.checkbox("凡例を表示", value=True)

# show legend
if show_legend:
    cols = st.columns(3)
    cols[0].markdown(f'<div style="background:{STATUS_COLORS["確保"]};padding:6px;border-radius:8px;font-weight:700">確保</div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div style="background:{STATUS_COLORS["抽選中"]};padding:6px;border-radius:8px;font-weight:700">抽選中</div>', unsafe_allow_html=True)
    cols[2].markdown(f'<div style="background:{STATUS_COLORS["中止"]};padding:6px;border-radius:8px;font-weight:700">中止</div>', unsafe_allow_html=True)

# ---------- カレンダーヘッダー（曜日） ----------
st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
weekdays = ["日", "月", "火", "水", "木", "金", "土"]
cols = st.columns(7)
for i, day in enumerate(weekdays):
    with cols[i]:
        css_class = "sunday" if i == 0 else "saturday" if i == 6 else ""
        st.markdown(f"<div class='weekday-header {css_class}'>{day}</div>", unsafe_allow_html=True)

# build calendar grid
year, month = st.session_state.year_month
cal = calendar.Calendar(firstweekday=6)  # Sunday start
month_days = list(cal.itermonthdates(year, month))

# render month day cells
for wk in range(0, len(month_days), 7):
    week = month_days[wk:wk+7]
    st.markdown("<div class='week-row'>", unsafe_allow_html=True)
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            css_class = "sunday" if i == 0 else "saturday" if i == 6 else ""
            if day == today:
                css_class += " today"
            if day.month != month:
                css_class += " other-month"
            st.markdown(f"<div class='day-cell {css_class}'>", unsafe_allow_html=True)

            # 日付バッジ（常に表示）
            st.markdown(f"<div class='day-number'>{day.day}</div>", unsafe_allow_html=True)

            # 当月以外は薄く表示して日付文字を右寄せで表示
            if day.month != month:
                st.markdown(f"<div class='day-header'><div style='color:#999;text-align:left;padding-left:44px'>{day.strftime('%Y-%m-%d')}</div></div>", unsafe_allow_html=True)
            else:
                # クリックで編集モーダルを開く（見た目はバッジで表現）
                day_key = f"day-{day.isoformat()}"
                if st.button("", key=day_key):
                    st.session_state.selected_id = None
                    st.session_state.selected_date = day
                    st.session_state.show_modal = True

            # show events for this day
            day_entries = df.copy()
            if not day_entries.empty:
                # parse dates safely to avoid overflow when csv contains large numeric timestamps
                day_entries['date'] = safe_parse_date_series(day_entries['date'])
                day_entries = day_entries[day_entries['date'] == day]
                if f_facility:
                    day_entries = day_entries[day_entries['facility'].str.contains(f_facility, na=False)]
                if f_nick:
                    day_entries = day_entries[day_entries['nick'].str.contains(f_nick, na=False)]

            if not day_entries.empty:
                st.markdown("<div class='day-events'>", unsafe_allow_html=True)
                for idx, ev in day_entries.sort_values(["start_time"]).iterrows():
                    color = STATUS_COLORS.get(ev["status"], "#eeeeee")
                    pill_html = (
                        f"<div class='event-pill' style='background:{color};'>"
                        f"<div class='event-time'>{ev['start_time']}-{ev['end_time']}</div>"
                        f"<div class='event-meta'>{ev['facility']}</div>"
                        f"<div class='event-status'>{ev['status']}</div>"
                        f"</div>"
                    )
                    st.markdown(pill_html, unsafe_allow_html=True)
                    key = f"view-{ev['id']}"
                    if st.button("編集", key=key):
                        st.session_state.selected_id = ev["id"]
                        st.session_state.selected_date = day
                        st.session_state.show_modal = True
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # close calendar-grid

# ---------- Editor modal (side area) ----------
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

def render_edit_modal(sel_date, sel_id=None):
    # load fresh df
    df_local = load_entries()
    if sel_id:
        row = df_local[df_local["id"] == sel_id].iloc[0]
        facility_val = row["facility"]
        start_val = row["start_time"]
        end_val = row["end_time"]
        nick_val = row["nick"]
        status_val = row["status"]
    else:
        facility_val = ""
        start_val = "09:00"
        end_val = "10:00"
        nick_val = ""
        status_val = "抽選中"

    with st.modal("予約編集", clear_on_close=False):
        st.markdown(f"### {sel_date.isoformat()} の予約編集")
        with st.form("edit_form"):
            facility = st.text_input("施設名（直接入力）", value=facility_val)
            col_a, col_b = st.columns(2)
            with col_a:
                start_time = st.text_input("開始時刻（HH:MM、10分単位）", value=start_val)
            with col_b:
                end_time = st.text_input("終了時刻（HH:MM、10分単位）", value=end_val)
            nick = st.text_input("担当者（ニックネーム）", value=nick_val)
            status = st.selectbox("状態", options=["確保","抽選中","中止"], index=["確保","抽選中","中止"].index(status_val) if status_val in ["確保","抽選中","中止"] else 1)
            submitted = st.form_submit_button("保存")
            delete_btn = st.form_submit_button("削除")
            cancel_btn = st.form_submit_button("キャンセル")

            if submitted:
                if not facility.strip():
                    st.error("施設名を入力してください。")
                elif not valid_time_str(start_time) or not valid_time_str(end_time):
                    st.error("時刻はHH:MM形式かつ10分単位で入力してください（例 09:10）。")
                elif start_time >= end_time:
                    st.error("開始時刻は終了時刻より前にしてください。")
                else:
                    if overlaps(df_local, sel_date, start_time, end_time, exclude_id=sel_id):
                        st.warning("時間が他の予定と重複しています。問題なければ保存してください（重複検出のみ）。")
                    if sel_id:
                        df_local.loc[df_local["id"] == sel_id, ["facility","date","start_time","end_time","nick","status"]] = [
                            facility, sel_date.isoformat(), start_time, end_time, nick, status
                        ]
                    else:
                        new_id = str(uuid.uuid4())
                        new_row = {
                            "id": new_id,
                            "facility": facility,
                            "date": sel_date.isoformat(),
                            "start_time": start_time,
                            "end_time": end_time,
                            "nick": nick,
                            "status": status,
                            "created_at": datetime.now().isoformat()
                        }
                        df_local = pd.concat([df_local, pd.DataFrame([new_row])], ignore_index=True)
                    save_entries(df_local)
                    st.success("保存しました。")
                    st.session_state.show_modal = False
                    st.experimental_rerun()

            if delete_btn and sel_id:
                df_local = df_local[df_local["id"] != sel_id]
                save_entries(df_local)
                st.success("削除しました。")
                st.session_state.show_modal = False
                st.experimental_rerun()

            if cancel_btn:
                st.session_state.show_modal = False
                st.experimental_rerun()

# ---------- Footer / tips ----------
st.markdown("---")
st.markdown("#### 操作メモ")
st.markdown("- 日付を押すとその日付で新規登録できます。")
st.markdown("- 時刻はHH:MM形式で**10分単位**（例 09:10, 14:30）で入力してください。")
st.markdown("- データはリポジトリの `data/entries.csv` に保存されます。バックアップを定期的に行ってください。")
