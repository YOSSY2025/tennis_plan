import streamlit as st
from st_aggrid import AgGrid
from datetime import date, datetime, timedelta
from streamlit_fullcalendar import FullCalendar

# -------------------------------
# データサンプル
# サンプル予約データ
# -------------------------------
# 予約データ（本来はCSVなどから読み込む）
reservations = [
    {"date": date(2025, 11, 7), "status": "確保", "participants": 3, "absent": 1},
    {"date": date(2025, 11, 10), "status": "抽選中", "participants": 0, "absent": 0},
@ -14,62 +13,44 @@ reservations = [

# ステータス別カラー
status_color = {
    "確保": "lightblue",
    "確保": "blue",
    "抽選中": "yellow",
    "中止": "lightgrey",
    "完了": "lightgrey"
    "中止": "grey",
    "完了": "grey"
}

# -------------------------------
# ヘッダー
# タイトル
# -------------------------------
st.markdown(
    "<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True
)
st.markdown("<h2>🎾 テニスコート予約管理</h2>", unsafe_allow_html=True)

# -------------------------------
# カレンダー生成
# カレンダーイベント作成
# -------------------------------
st.subheader("📅 11月の予約状況")

# カレンダー表示（簡易版：日付と情報をテーブル化）
import pandas as pd

# 月の初日・最終日
year = 2025
month = 11
first_day = date(year, month, 1)
last_day = date(year, month, 30)

calendar_list = []
for single_date in pd.date_range(first_day, last_day):
    # 該当日の予約
    res = next((r for r in reservations if r["date"] == single_date.date()), None)
    if res:
        cell_text = f"{res['status']}\n〇{res['participants']} ×{res['absent']}"
        cell_color = status_color.get(res["status"], "white")
    else:
        cell_text = ""
        cell_color = "white"
    calendar_list.append({
        "日付": single_date.date(),
        "予約状況": cell_text,
        "color": cell_color
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

calendar_df = pd.DataFrame(calendar_list)
# -------------------------------
# カレンダー表示
# -------------------------------
FullCalendar(
    events=events,
    initial_view="dayGridMonth",   # 月表示
    selectable=True
)

# AgGridでカラフル表示
from st_aggrid import AgGrid, GridOptionsBuilder
gb = GridOptionsBuilder.from_dataframe(calendar_df)
gb.configure_columns(["日付", "予約状況"])
gb.configure_default_column(editable=False)
# 条件付きで色付け
cells_styles = []
for idx, row in calendar_df.iterrows():
    cells_styles.append({
        "rowIndex": idx,
        "backgroundColor": row["color"]
    })
grid_options = gb.build()
AgGrid(calendar_df, gridOptions=grid_options)
# -------------------------------
# 日付クリック時の処理は次ステップで追加
# -------------------------------
st.info("日付クリックで予約詳細モーダルを表示予定")