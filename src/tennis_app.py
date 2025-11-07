import streamlit as st
import pandas as pd
from datetime import datetime, date

# =========================
# CSVロード/保存
# =========================
DATA_PATH = "../data/reservations.csv"

def load_reservations():
    try:
        return pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "date","facility","status","start_hour","start_minute",
            "end_hour","end_minute","participants","absent"
        ])

def save_reservations(df):
    df.to_csv(DATA_PATH, index=False)

df_res = load_reservations()

# =========================
# ヘルパー
# =========================
def status_color(status):
    if status=="確保":
        return "green"
    elif status=="抽選中":
        return "yellow"
    elif status in ["中止","完了"]:
        return "lightgray"
    else:
        return "white"

# =========================
# 日付クリック（予約登録）
# =========================
st.title("🎾 テニスコート予約管理")

# 月表示（簡易）
selected_date = st.date_input("予約日を選択", value=date.today())

# 過去日付は自動で完了
df_res["date"] = pd.to_datetime(df_res["date"]).dt.date
df_res.loc[df_res["date"] < date.today(), "status"] = "完了"

# カレンダー風表示（簡易テーブル）
st.subheader("予約状況（月表示）")
df_show = df_res[pd.to_datetime(df_res["date"]).dt.month == selected_date.month]

df_show_display = df_show.copy()
df_show_display["時間"] = df_show_display["start_hour"].astype(str).str.zfill(2) + ":" + \
                          df_show_display["start_minute"].astype(str).str.zfill(2) + "〜" + \
                          df_show_display["end_hour"].astype(str).str.zfill(2) + ":" + \
                          df_show_display["end_minute"].astype(str).str.zfill(2)
df_show_display["参加人数"] = df_show_display["participants"].apply(lambda x: len(eval(x)) if x else 0)
df_show_display["不参加人数"] = df_show_display["absent"].apply(lambda x: len(eval(x)) if x else 0)
df_show_display = df_show_display[["date","facility","時間","status","参加人数","不参加人数"]]
st.dataframe(df_show_display.style.applymap(lambda v: status_color(v) if v in ["確保","抽選中","中止","完了"] else "", subset=["status"]))

# =========================
# 予約登録
# =========================
st.subheader("予約登録")
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

start_time_str = f"{start_hour:02d}:{start_minute:02d}"
end_time_str = f"{end_hour:02d}:{end_minute:02d}"
st.write(f"開始: {start_time_str} / 終了: {end_time_str}")

status = st.selectbox("ステータス", ["確保","抽選中","中止"])

if st.button("登録"):
    df_res = pd.concat([df_res, pd.DataFrame([{
        "date": selected_date,
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
    st.success(f"{selected_date} に {facility} を登録しました")

# =========================
# 参加表明
# =========================
st.subheader("参加表明")
if not df_res.empty:
    reservation_idx = st.selectbox("予約を選択", df_res.index, format_func=lambda x: f"{df_res.loc[x,'date']} {df_res.loc[x,'facility']}")
    if reservation_idx is not None:
        name = st.text_input("ニックネーム")
        attendance = st.selectbox("参加状況", ["参加","不参加"])
        if st.button("登録（参加表明）", key="participation"):
            participants = eval(df_res.at[reservation_idx,"participants"]) if df_res.at[reservation_idx,"participants"] else []
            absent = eval(df_res.at[reservation_idx,"absent"]) if df_res.at[reservation_idx,"absent"] else []
            # 既存削除
            if name in participants: participants.remove(name)
            if name in absent: absent.remove(name)
            # 新規追加
            if attendance=="参加":
                participants.append(name)
            else:
                absent.append(name)
            df_res.at[reservation_idx,"participants"] = str(participants)
            df_res.at[reservation_idx,"absent"] = str(absent)
            save_reservations(df_res)
            st.success(f"{name} の参加表明を登録しました")
