import streamlit as st
import pandas as pd
from datetime import date, timedelta
from streamlit_calendar import calendar

# サンプル予約データ
reservations = [
    {"date": date(2025,11,7),  "facility":"けやきネット","status":"確保", "participants":["Alice","Bob"], "absent":["Charlie"]},
    {"date": date(2025,11,10), "facility":"駒沢","status":"抽選中", "participants":[], "absent":[]},
]

# ステータスカラー
status_color = {
    "確保": {"bg":"#90ee90","text":"black"},
    "抽選中": {"bg":"#ffd966","text":"black"},
    "中止": {"bg":"#d3d3d3","text":"black"},
    "完了": {"bg":"#d3d3d3","text":"black"}
}

# タイトル
st.markdown("<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True)

# カレンダー用イベント
events = []
for r in reservations:
    start_str = r["date"].strftime("%Y-%m-%d")
    end_str = (r["date"]+timedelta(days=1)).strftime("%Y-%m-%d")
    title_str = f"{r['status']} 〇{len(r['participants'])} ×{len(r['absent'])}"
    color = status_color.get(r["status"], {"bg":"#FFFFFF","text":"black"})
    events.append({
        "title": title_str,
        "start": start_str,
        "end": end_str,
        "backgroundColor": color["bg"],
        "borderColor": color["bg"],
        "textColor": color["text"]
    })

# カレンダー表示
cal_state = calendar(
    events=events,
    options={
        "initialView":"dayGridMonth",
        "selectable":True,
        "headerToolbar":{"left":"prev,next today","center":"title","right":""}
    },
    key="reservation_calendar"
)

# 日付クリックやイベントクリック
if cal_state:
    callback = cal_state.get("callback")
    if callback == "dateClick":
        clicked_date = cal_state["dateClick"]["date"]
        st.info(f"📅 {clicked_date} の予約を確認/登録")
        # モーダル風で詳細表示
        facility = st.text_input("施設名")
        start_time = st.time_input("開始時間")
        end_time = st.time_input("終了時間")
        status = st.selectbox("ステータス", ["確保","抽選中","中止"])
        if st.button("登録"):
            st.success(f"{clicked_date} に {facility} を登録しました")
    elif callback == "eventClick":
        ev = cal_state["eventClick"]["event"]
        st.info(f"イベント選択：{ev['title']}")
        # 参加表明管理
        st.write("参加表明")
        nick = st.text_input("ニックネーム")
        part = st.radio("参加状況", ["参加","不参加"])
        if st.button("反映"):
            st.success(f"{nick} は {part} に設定されました")
