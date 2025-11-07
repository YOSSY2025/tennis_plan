import streamlit as st
import pandas as pd
import os
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar

# ===== CSVパス =====
CSV_PATH = "../data/reservations.csv"

# ===== データフォルダ・CSV初期化 =====
if not os.path.exists("../data"):
    os.makedirs("../data")

if not os.path.exists(CSV_PATH):
    df_init = pd.DataFrame(columns=["date","facility","status","start_hour","start_minute","end_hour","end_minute","participants","absent"])
    df_init.to_csv(CSV_PATH, index=False)

# ===== CSV読み書き関数 =====
def load_reservations():
    df = pd.read_csv(CSV_PATH)
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['participants'] = df['participants'].fillna("").apply(lambda x: x.split(';') if x else [])
    df['absent'] = df['absent'].fillna("").apply(lambda x: x.split(';') if x else [])
    return df

def save_reservations(df):
    df_to_save = df.copy()
    df_to_save['participants'] = df_to_save['participants'].apply(lambda x: ";".join(x))
    df_to_save['absent'] = df_to_save['absent'].apply(lambda x: ";".join(x))
    df_to_save.to_csv(CSV_PATH, index=False)

# ===== ステータスカラー =====
status_color = {
    "確保": {"bg":"#90ee90","text":"black"},
    "抽選中": {"bg":"#ffd966","text":"black"},
    "中止": {"bg":"#d3d3d3","text":"black"},
    "完了": {"bg":"#d3d3d3","text":"black"}
}

# ===== Streamlit タイトル =====
st.markdown("<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True)

# ===== データ読み込み =====
df_res = load_reservations()

# ===== カレンダー表示用イベント生成 =====
events = []
for idx, r in df_res.iterrows():
    start_str = r["date"].strftime("%Y-%m-%d")
    end_str = (r["date"] + timedelta(days=1)).strftime("%Y-%m-%d")
    title_str = f"{r['status']} 〇{len(r['participants'])} ×{len(r['absent'])}"
    color = status_color.get(r["status"], {"bg":"#FFFFFF","text":"black"})
    events.append({
        "id": idx,
        "title": title_str,
        "start": start_str,
        "end": end_str,
        "backgroundColor": color["bg"],
        "borderColor": color["bg"],
        "textColor": color["text"]
    })

# ===== カレンダー表示 =====
cal_state = calendar(
    events=events,
    options={
        "initialView":"dayGridMonth",
        "selectable":True,
        "headerToolbar":{"left":"prev,next today","center":"title","right":""}
    },
    key="reservation_calendar"
)

# ===== 日付クリックで予約登録 =====
if cal_state:
    callback = cal_state.get("callback")
    if callback == "dateClick":
        clicked_date = cal_state["dateClick"]["date"]
        st.info(f"📅 {clicked_date} の予約を確認/登録")

        facility = st.text_input("施設名")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            start_hour = st.selectbox("開始時（時）", list(range(0,24)), key="sh")
        with col2:
            start_minute = st.selectbox("開始分", [0,10,20,30,40,50], key="sm")
        with col3:
            end_hour = st.selectbox("終了時（時）", list(range(0,24)), key="eh")
        with col4:
            end_minute = st.selectbox("終了分", [0,10,20,30,40,50], key="em")

        status = st.selectbox("ステータス", ["確保","抽選中","中止"])

        if st.button("登録"):
            df_res = pd.concat([df_res, pd.DataFrame([{
                "date": datetime.strptime(clicked_date, "%Y-%m-%d").date(),
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
            st.success(f"{clicked_date} に {facility} を登録しました")

    # ===== イベントクリックで参加表明 =====
    elif callback == "eventClick":
        ev = cal_state["eventClick"]["event"]
        idx = ev["id"]
        r = df_res.loc[idx]
        st.info(f"イベント選択：{r['facility']} ({r['status']})")

        nick = st.text_input("ニックネーム")
        part = st.radio("参加状況", ["参加","不参加"])

        if st.button("反映"):
            if part == "参加":
                if nick not in r["participants"]:
                    r["participants"].append(nick)
                if nick in r["absent"]:
                    r["absent"].remove(nick)
            else:
                if nick not in r["absent"]:
                    r["absent"].append(nick)
                if nick in r["participants"]:
                    r["participants"].remove(nick)
            df_res.loc[idx] = r
            save_reservations(df_res)
            st.success(f"{nick} は {part} に設定されました")
