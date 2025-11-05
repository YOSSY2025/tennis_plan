# tennis_app_calendar.py
# Run: streamlit run tennis_app_calendar.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from your_module import safe_parse_date_series  # Assuming safe_parse_date_series is defined globally
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
    # read everything as string to avoid pandas auto-parsing surprises
    return pd.read_csv(DATA_FILE, dtype=str)


def safe_parse_date_series(s):
    """Parse a Series containing dates that may be ISO strings or epoch numbers in s/ms/us/ns.
    Returns a Series of python date objects (or NaT converted to NaN via pandas NaT -> None).
    """
    s = s.fillna("").astype(str).str.strip()
    is_digits = s.str.fullmatch(r"\d+")
    parsed = pd.Series(pd.NaT, index=s.index, dtype='datetime64[ns]')
    if is_digits.any():
        nums = pd.to_numeric(s[is_digits], errors='coerce')
        if not nums.empty:
            maxv = int(nums.max())
            if maxv >= 10**17:
                unit = 'ns'
            elif maxv >= 10**14:
                unit = 'us'
            elif maxv >= 10**11:
                unit = 'ms'
            else:
                unit = 's'
            parsed.loc[is_digits] = pd.to_datetime(nums.astype('int64'), unit=unit, errors='coerce')
    non_digits = ~is_digits
    if non_digits.any():
        parsed.loc[non_digits] = pd.to_datetime(s[non_digits].replace('', pd.NaT), errors='coerce')
    return parsed.dt.date

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
                # show events for this day and render modal

def overlaps(existing_df, target_date, start, end, exclude_id=None):
    """同じ施設で時間帯重複チェック（単純判定）"""
                    # use global safe parser

# ---------- レイアウトCSS ----------
st.markdown("""
<style>
:root{--mint:#A8E6CF; --orange:#FFB997; --card:#F8FFF3; --muted:#6b6b6b;}
body { background-color: #ffffff; }
.header { display:flex; align-items:center; justify-content:space-between; }
.app-title { font-size:22px; font-weight:700; color:#116466; }
.sub { color:var(--muted); font-size:13px; }
/* カレンダーグリッド */
.calendar-grid { border: 1px solid #e0e0e0; margin-top: 1rem; }
.week-row { display: flex; border-bottom: 1px solid #e0e0e0; }
.week-row:last-child { border-bottom: none; }
.day-cell { 
    padding: 6px; 
    background: #fff; 
    border-right: 1px solid #e0e0e0;
    min-height: 100px;
    flex: 1;
    position: relative;
                        key = f"view-{ev['id']}"
                        if st.button("編集", key=key):
                            render_edit_modal(day, ev["id"])
    font-weight: 700;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
}
.sunday { color: #e74c3c; }
.saturday { color: #3498db; }
/* イベントスタイル */
.event-pill {
    padding: 4px 6px;
    border-radius: 4px;
    margin-bottom: 4px;
    font-size: 12px;
    line-height: 1.4;
}
.event-time {
    font-weight: 700;
    font-size: 11px;
}
.event-status {
    font-size: 11px;
    opacity: 0.9;
}
.event-meta {
    font-size: 11px;
    color: #333;
    margin-top: 2px;
}
/* ボタン */
.day-cell button.date-btn {
    background: none !important;
    border: none !important;
    padding: 4px !important;
    margin: 0 !important;
    font-size: 14px !important;
    color: inherit !important;
    cursor: pointer;
    display: block;
    width: 100%;
    text-align: center !important;
}
.day-cell button.date-btn:hover {
    background: #f8f9fa !important;
}
.other-month {
    color: #bbb !important;
    background: #fafafa;
}
.today button.date-btn {
    font-weight: 700 !important;
    color: #fff !important;
    background: #116466 !important;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    line-height: 24px;
    margin: 0 auto !important;
}
.small { font-size: 12px; color: #666; }
@media (max-width:600px){
  .app-title { font-size:18px; }
  .day-cell { min-height: 80px; padding: 4px; }
  .event-pill { font-size: 11px; }
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
            
            # 日付表示（当月のみクリック可能）
            if day.month != month:
                st.markdown(f"<div style='text-align:center'>{day.day}</div>", unsafe_allow_html=True)
            else:
                day_key = f"day-{day.isoformat()}"
                if st.button(str(day.day), key=day_key, kwargs={"class": "date-btn"}):
                    st.session_state.selected_id = None
                    st.session_state.selected_date = day
                    st.session_state.open_editor = True

            # show events for this day
            day_entries = df.copy()
            if not day_entries.empty:
                # safe parse 'date' column: handle ISO strings or epoch numbers (s/ms/us/ns)
                def safe_parse_date_series(s):
                    s = s.fillna("").astype(str).str.strip()
                    # mask of pure digits
                    is_digits = s.str.fullmatch(r"\d+")
                    parsed = pd.Series(pd.NaT, index=s.index, dtype='datetime64[ns]')
                    if is_digits.any():
                        nums = pd.to_numeric(s[is_digits], errors='coerce')
                        if not nums.empty:
                            maxv = int(nums.max())
                            # decide unit
                            if maxv >= 10**17:
                                unit = 'ns'
                            elif maxv >= 10**14:
                                unit = 'us'
                            elif maxv >= 10**11:
                                unit = 'ms'
                            else:
                                unit = 's'
                            parsed.loc[is_digits] = pd.to_datetime(nums.astype('int64'), unit=unit, errors='coerce')
                    # parse non-digit strings
                    non_digits = ~is_digits
                    if non_digits.any():
                        parsed.loc[non_digits] = pd.to_datetime(s[non_digits].replace('', pd.NaT), errors='coerce')
                    return parsed.dt.date

                # if 'date' column missing, create empty
                if 'date' not in day_entries.columns:
                    day_entries['date'] = ""
                day_entries['date'] = safe_parse_date_series(day_entries['date'])
                day_entries = day_entries[day_entries['date'] == day]
                if f_facility:
                    day_entries = day_entries[day_entries['facility'].str.contains(f_facility, na=False)]
                if f_nick:
                    day_entries = day_entries[day_entries['nick'].str.contains(f_nick, na=False)]

            if not day_entries.empty:
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
                        st.session_state.open_editor = True

            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # close calendar-grid

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
st.markdown("- 日付を押すとその日付で新規登録できます。")
st.markdown("- 時刻はHH:MM形式で**10分単位**（例 09:10, 14:30）で入力してください。")
st.markdown("- データはリポジトリの `data/entries.csv` に保存されます。バックアップを定期的に行ってください。")