# tennis_app_calendar.py
# Run: streamlit run tennis_app_calendar.py
import streamlit as st
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

def valid_time_str(t):
    if not isinstance(t, str): return False
    m = re.match(TIME_REGEX, t.strip())
    if not m: return False
    hh, mm = int(m.group(1)), int(m.group(2))
    return (mm % 10) == 0

def overlaps(existing_df, target_date, start, end, exclude_id=None):
    """同じ施設で時間帯重複チェック（単純判定）"""
    ed = existing_df.copy()
    ed["date"] = pd.to_datetime(ed["date"]).dt.date
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
.day-cell { border-radius:8px; padding:8px; margin:6px 0; background: #fff; box-shadow: 0 6px 14px rgba(0,0,0,0.04); }
.event-pill { padding:6px 8px; border-radius:8px; color:#111; font-weight:600; margin-bottom:6px; display:block; }
.small { font-size:13px; color:#444; }
@media (max-width:600px){
  .app-title { font-size:18px; }
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

# build calendar grid
year, month = st.session_state.year_month
cal = calendar.Calendar(firstweekday=6)  # Sunday start
month_days = list(cal.itermonthdates(year, month))

# render month day cells
for wk in range(0, len(month_days), 7):
    week = month_days[wk:wk+7]
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            # header for each day
            if day.month != month:
                st.markdown(f"<div class='small' style='color:#bbb'>{day.day}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='small' style='font-weight:700'>{day.day} ({calendar.day_name[day.weekday()][:3]})</div>", unsafe_allow_html=True)
            # card for events
            st.markdown("<div class='day-cell'>", unsafe_allow_html=True)
            # show events for this day
            day_entries = df.copy()
            if not day_entries.empty:
                day_entries['date'] = pd.to_datetime(day_entries['date']).dt.date
                day_entries = day_entries[day_entries['date'] == day]
                if f_facility:
                    day_entries = day_entries[day_entries['facility'].str.contains(f_facility, na=False)]
                if f_nick:
                    day_entries = day_entries[day_entries['nick'].str.contains(f_nick, na=False)]
            if day_entries.empty:
                st.markdown("<div class='small' style='color:#999'>予定なし</div>", unsafe_allow_html=True)
            else:
                # list items (max 4, show more link)
                for idx, ev in day_entries.sort_values(["start_time"]).iterrows():
                    color = STATUS_COLORS.get(ev["status"], "#eeeeee")
                    text = f'{ev["start_time"]}-{ev["end_time"]} {ev["facility"]} / {ev["nick"]}'
                    # clickable: use st.button with unique key to open editor
                    key = f"view-{ev['id']}"
                    if st.button(text, key=key):
                        st.session_state.selected_id = ev["id"]
                        st.session_state.selected_date = day
                        st.session_state.open_editor = True
            # add new button
            add_key = f"add-{day.isoformat()}"
            if st.button("＋ 追加", key=add_key):
                st.session_state.selected_id = None
                st.session_state.selected_date = day
                st.session_state.open_editor = True
            st.markdown("</div>", unsafe_allow_html=True)

# ---------- Editor modal (side area) ----------
if "open_editor" not in st.session_state:
    st.session_state.open_editor = False

if st.session_state.open_editor:
    st.markdown("---")
    sel_date = st.session_state.get("selected_date", date.today())
    st.markdown(f"### {sel_date.isoformat()} の予約編集")
    # load fresh df
    df = load_entries()
    # if editing existing
    sel_id = st.session_state.get("selected_id", None)
    if sel_id:
        row = df[df["id"] == sel_id].iloc[0]
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
            # validation
            if not facility.strip():
                st.error("施設名を入力してください。")
            elif not valid_time_str(start_time) or not valid_time_str(end_time):
                st.error("時刻はHH:MM形式かつ10分単位で入力してください（例 09:10）。")
            else:
                # check start < end
                if start_time >= end_time:
                    st.error("開始時刻は終了時刻より前にしてください。")
                else:
                    # overlap check
                    if overlaps(df, sel_date, start_time, end_time, exclude_id=sel_id):
                        st.warning("時間が他の予定と重複しています。問題なければ保存してください（重複検出のみ）。")
                    # save
                    if sel_id:
                        df.loc[df["id"] == sel_id, ["facility","date","start_time","end_time","nick","status"]] = [
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
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_entries(df)
                    st.success("保存しました。")
                    st.session_state.open_editor = False
                    st.session_state.refresh += 1
                    st.experimental_rerun()

        if delete_btn and sel_id:
            df = df[df["id"] != sel_id]
            save_entries(df)
            st.success("削除しました。")
            st.session_state.open_editor = False
            st.experimental_rerun()

        if cancel_btn:
            st.session_state.open_editor = False
            st.experimental_rerun()

# ---------- Footer / tips ----------
st.markdown("---")
st.markdown("#### 操作メモ")
st.markdown("- 日付の「＋追加」を押すとその日付で新規登録できます。")
st.markdown("- 時刻はHH:MM形式で**10分単位**（例 09:10, 14:30）で入力してください。")
st.markdown("- データはリポジトリの `data/entries.csv` に保存されます。バックアップを定期的に行ってください。")
