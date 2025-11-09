import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, time, timedelta
from streamlit_calendar import calendar

# ===== CSVパス =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "reservations.csv")

# ===== データフォルダ作成 =====
if not os.path.exists(os.path.join(BASE_DIR, "data")):
    os.makedirs(os.path.join(BASE_DIR, "data"))

if not os.path.exists(CSV_PATH):
    df_init = pd.DataFrame(columns=[
        "date","facility","status","start_hour","start_minute",
        "end_hour","end_minute","participants","absent"
    ])
    df_init.to_csv(CSV_PATH, index=False)

# ===== CSV読み書き関数 =====
def load_reservations():
    df = pd.read_csv(CSV_PATH)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    else:
        df["date"] = []
    df["participants"] = df["participants"].fillna("").apply(lambda x: x.split(";") if x else [])
    df["absent"] = df["absent"].fillna("").apply(lambda x: x.split(";") if x else [])
    return df

def save_reservations(df):
    df_to_save = df.copy()
    df_to_save["date"] = df_to_save["date"].apply(lambda d: d.strftime("%Y-%m-%d") if isinstance(d, (date, datetime)) else "")
    df_to_save["participants"] = df_to_save["participants"].apply(lambda lst: ";".join(lst) if isinstance(lst, list) else "")
    df_to_save["absent"] = df_to_save["absent"].apply(lambda lst: ";".join(lst) if isinstance(lst, list) else "")
    df_to_save.to_csv(CSV_PATH, index=False)

# ===== ステータスカラー =====
status_color = {
    "確保": {"bg":"#90ee90","text":"black"},
    "抽選中": {"bg":"#ffd966","text":"black"},
    "中止": {"bg":"#d3d3d3","text":"black"},
    "完了": {"bg":"#d3d3d3","text":"black"}
}

# ===== JST変換 =====
def to_jst_date(iso_str):
    """ISO形式の日付文字列をJSTのdate型に変換"""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (dt + timedelta(hours=9)).date()
    except Exception:
        if isinstance(iso_str, date):
            return iso_str
        return datetime.strptime(str(iso_str)[:10], "%Y-%m-%d").date()

# ===== タイトル =====
st.markdown("<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True)

# ===== データ読み込み =====
df_res = load_reservations()

# ===== カレンダーイベント生成 =====
events = []
for idx, r in df_res.iterrows():
    if pd.isna(r["date"]):
        continue

    start_dt = datetime.combine(r["date"], time(int(r.get("start_hour",0)), int(r.get("start_minute",0))))
    end_dt = datetime.combine(r["date"], time(int(r.get("end_hour",0)), int(r.get("end_minute",0))))

    title_str = f"{r['facility'][:6]} {r['status']} 〇{len(r['participants'])}×{len(r['absent'])}"
    color = status_color.get(r["status"], {"bg":"#FFFFFF","text":"black"})
    events.append({
        "id": idx,
        "title": title_str,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "backgroundColor": color["bg"],
        "borderColor": color["bg"],
        "textColor": color["text"]
    })

# ===== カレンダー表示 =====
cal_state = calendar(
    events=events,
    options={
        "initialView": "dayGridMonth",
        "selectable": True,
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": ""}
    },
    key="reservation_calendar"
)

# ===== イベント操作 =====
if cal_state:
    callback = cal_state.get("callback")

    # ---- 日付クリック ----
    if callback == "dateClick":
        clicked_date = cal_state["dateClick"]["date"]
        clicked_date_jst = to_jst_date(clicked_date)
        st.info(f"📅 {clicked_date_jst} の予約を確認/登録")

        facility = st.text_input("施設名", key=f"facility_{clicked_date}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            start_hour = st.selectbox("開始時", list(range(0,24)), key=f"sh_{clicked_date}")
        with col2:
            start_minute = st.selectbox("開始分", [0,10,20,30,40,50], key=f"sm_{clicked_date}")
        with col3:
            end_hour = st.selectbox("終了時", list(range(0,24)), key=f"eh_{clicked_date}")
        with col4:
            end_minute = st.selectbox("終了分", [0,10,20,30,40,50], key=f"em_{clicked_date}")

        status = st.selectbox("ステータス", ["確保","抽選中","中止"], key=f"st_{clicked_date}")

        if st.button("登録", key=f"reg_{clicked_date}"):
            df_res = pd.concat([df_res, pd.DataFrame([{
                "date": clicked_date_jst,
                "facility": facility,
                "status": status,
                "start_hour": start_hour,
                "start_minute": start_minute,
                "end_hour": end_hour,
                "end_minute": end_minute,
                "participants": [],
                "absent": []
            }])], ignore_index=True)
            save_reservations(df_res)
            st.success(f"{clicked_date_jst} に {facility} を登録しました")
            st.experimental_rerun()

    # ---- イベントクリック ----
    elif callback == "eventClick":
        ev = cal_state["eventClick"]["event"]
        idx = int(ev["id"])
        r = df_res.loc[idx]
        event_date = to_jst_date(r["date"])
        st.info(f"イベント選択：{event_date}\n{r['facility']} ({r['status']})")

        nick = st.text_input("ニックネーム", key=f"nick_{idx}")
        part = st.radio("参加状況", ["参加", "不参加"], key=f"part_{idx}")

        if st.button("反映", key=f"apply_{idx}"):
            participants = list(r["participants"]) if isinstance(r["participants"], list) else []
            absent = list(r["absent"]) if isinstance(r["absent"], list) else []

            if nick in participants:
                participants.remove(nick)
            if nick in absent:
                absent.remove(nick)

            if part == "参加":
                participants.append(nick)
            else:
                absent.append(nick)

            df_res.at[idx, "participants"] = participants
            df_res.at[idx, "absent"] = absent
            save_reservations(df_res)
            st.success(f"{nick} は {part} に設定されました")
            st.experimental_rerun()
