import streamlit as st
import pandas as pd
from datetime import datetime, date

# -------------------------------
# 各画面定義
# -------------------------------

def show_home():
    st.title("🎾 テニスコート予約管理")
    st.write("以下のメニューから選択してください。")
    if st.button("📅 予約カレンダーを開く"):
        st.session_state.page = "calendar"
    if st.button("🧍‍♂️ 参加表明画面を開く"):
        st.session_state.page = "participation"
    if st.button("🎯 抽選期間を確認する"):
        st.session_state.page = "lottery"


def show_calendar():
    st.title("📅 予約カレンダー")
    st.write("日付をクリックして予約詳細を確認・編集できます。")

    selected_date = st.date_input("日付を選択", date.today())
    if st.button("選択した日の予約を見る"):
        st.session_state.selected_date = selected_date
        st.session_state.page = "reservation_modal"

    if st.button("🏠 トップへ戻る"):
        st.session_state.page = "home"


def show_reservation_modal():
    st.title("📋 予約詳細")
    selected_date = st.session_state.get("selected_date", date.today())
    st.write(f"選択日：{selected_date}")

    with st.form("reservation_form"):
        court = st.selectbox("コート番号", ["A", "B", "C"])
        start_time = st.time_input("開始時刻")
        end_time = st.time_input("終了時刻")
        note = st.text_area("備考")

        submitted = st.form_submit_button("登録")
        if submitted:
            st.success("✅ 登録が完了しました！")

    if st.button("⬅ カレンダーに戻る"):
        st.session_state.page = "calendar"


def show_participation():
    st.title("🧍‍♀️ 参加表明画面")
    df = pd.DataFrame({
        "日付": ["2025-11-10", "2025-11-17", "2025-11-24"],
        "コート": ["A", "B", "A"],
        "開始": ["9:00", "9:00", "10:00"],
        "終了": ["11:00", "11:00", "12:00"],
    })

    st.dataframe(df)

    st.write("参加・不参加を選択：")
    selected = st.selectbox("対象日を選択", df["日付"])
    status = st.radio("ステータス", ["参加", "不参加", "未定"])

    if st.button("更新"):
        st.success(f"{selected} を「{status}」に更新しました。")

    if st.button("🏠 トップへ戻る"):
        st.session_state.page = "home"


def show_lottery_periods():
    st.title("🎯 抽選期間確認")

    data = [
        {"id": 1, "name": "12月前半 抽選", "start_date": "2025-11-01", "end_date": "2025-11-10"},
        {"id": 2, "name": "12月後半 抽選", "start_date": "2025-11-15", "end_date": "2025-11-25"},
        {"id": 3, "name": "1月前半 抽選", "start_date": "2025-12-01", "end_date": "2025-12-10"},
    ]
    df = pd.DataFrame(data)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    now = datetime.now()

    def get_status(row):
        if row["start_date"] <= now <= row["end_date"]:
            return "応募中"
        elif now < row["start_date"]:
            return "未開始"
        else:
            return "終了"

    df["status"] = df.apply(get_status, axis=1)

    def highlight_status(row):
        color = ""
        if row["status"] == "応募中":
            color = "background-color: #d4edda;"
        elif row["status"] == "未開始":
            color = "background-color: #fff3cd;"
        else:
            color = "background-color: #f8d7da;"
        return [color] * len(row)

    st.dataframe(
        df.style.apply(highlight_status, axis=1)
                 .format({"start_date": lambda x: x.strftime("%Y-%m-%d"),
                          "end_date": lambda x: x.strftime("%Y-%m-%d")})
    )

    if st.button("🏠 トップへ戻る"):
        st.session_state.page = "home"


# -------------------------------
# メイン制御
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "calendar":
    show_calendar()
elif st.session_state.page == "reservation_modal":
    show_reservation_modal()
elif st.session_state.page == "participation":
    show_participation()
elif st.session_state.page == "lottery":
    show_lottery_periods()
