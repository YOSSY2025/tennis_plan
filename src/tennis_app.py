import streamlit as st
from streamlit_calendar import calendar
from datetime import date

# -------------------------------
# サンプル予約データ
# -------------------------------
reservations = [
    {"date": date(2025, 11, 7), "status": "確保", "participants": 3, "absent": 1},
    {"date": date(2025, 11, 10), "status": "抽選中", "participants": 0, "absent": 0},
    {"date": date(2025, 11, 15), "status": "中止", "participants": 0, "absent": 0},
]

# ステータス別カラー
status_color = {
    "確保": "lightgreen",
    "抽選中": "yellow",
    "中止": "lightgrey",
    "完了": "lightgrey"
}

# -------------------------------
# タイトル
# -------------------------------
st.markdown("<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True)

# -------------------------------
# カレンダー用データ作成
# -------------------------------
events = []
for r in reservations:
    events.append({
        "date": r["date"],
        "value": f"{r['status']} 〇{r['participants']} ×{r['absent']}",
        "color": status_color.get(r["status"], "white")
    })

# -------------------------------
# 月カレンダー表示
# -------------------------------
selected_date = calendar(events=events, format="month", height=600)

# -------------------------------
# 選択した日付の情報
# -------------------------------
if selected_date:
    st.write("選択日:", selected_date)
    event_for_day = next((e for e in events if e["date"] == selected_date), None)
    if event_for_day:
        st.write("予約情報:", event_for_day["value"])
    else:
        st.write("予約はありません")
