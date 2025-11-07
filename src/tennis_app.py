import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import calendar as cal

# -------------------------
# サンプル予約データ
# -------------------------
reservations = [
    {"date": date(2025, 11, 7), "status": "確保", "participants": 3, "absent": 1},
    {"date": date(2025, 11, 10), "status": "抽選中", "participants": 0, "absent": 0},
    {"date": date(2025, 11, 15), "status": "中止", "participants": 0, "absent": 0},
]

status_color = {
    "確保": "#90EE90",      # lightgreen
    "抽選中": "#FFFF99",    # yellow
    "中止": "#D3D3D3",      # lightgrey
    "完了": "#D3D3D3"       # lightgrey
}

# -------------------------
# 月の情報
# -------------------------
today = date.today()
year, month = today.year, today.month

_, num_days = cal.monthrange(year, month)

# 日付ごとの予約マッピング
res_map = {r["date"]: r for r in reservations}

# -------------------------
# タイトル
# -------------------------
st.markdown("<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True)
st.write(f"表示中: {year}年 {month}月")

# -------------------------
# カレンダーマトリクス生成
# -------------------------
weeks = []
week = []
first_weekday = cal.monthrange(year, month)[0]  # 月初の曜日（0=月曜）
day_counter = 1

# 最初の週の空白埋め
for i in range(first_weekday):
    week.append("")

while day_counter <= num_days:
    week.append(day_counter)
    if len(week) == 7:
        weeks.append(week)
        week = []
    day_counter += 1

# 最後の週の空白埋め
if week:
    while len(week) < 7:
        week.append("")
    weeks.append(week)

# -------------------------
# カレンダー表示
# -------------------------
for w in weeks:
    cols = st.columns(7)
    for i, day in enumerate(w):
        if day == "":
            cols[i].write(" ")
        else:
            current_date = date(year, month, day)
            r = res_map.get(current_date)
            if r:
                display_text = f"{r['status']} 〇{r['participants']} ×{r['absent']}"
                cols[i].button(display_text, key=str(current_date), help=str(current_date))
            else:
                cols[i].button(str(day), key=str(current_date), help=str(current_date))
