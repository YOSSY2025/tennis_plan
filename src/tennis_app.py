import streamlit as st
from datetime import date, datetime, timedelta
from streamlit_fullcalendar import FullCalendar

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
    "確保": "blue",
    "抽選中": "yellow",
    "中止": "grey",
    "完了": "grey"
}

# -------------------------------
# タイトル
# -------------------------------
st.markdown("<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True)

# -------------------------------
# カレンダーイベント作成
# -------------------------------
events = []
for r in reservations:
    start_str = r["date"].strftime("%Y-%m-%d")
    end_str = (r["date"] + timedelta(days=1)).strftime("%Y-%m-%d")
    title = f"{r['status']} 〇{r['participants']} ×{r['absent']}"
    color = status_color.get(r["status"], "white")
    
    events.append({
        "title": title,
        "start": start_str,
        "end": end_str,
        "color": color
    })

# -------------------------------
# カレンダー表示
# -------------------------------
FullCalendar(
    events=events,
    initial_view="dayGridMonth",   # 月表示
    selectable=True
)

# -------------------------------
# 日付クリック時の処理は次ステップで追加
# -------------------------------
st.info("日付クリックで予約詳細モーダルを表示予定")
