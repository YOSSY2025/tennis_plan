import streamlit as st
import pandas as pd

# アプリタイトル
st.set_page_config(page_title="テニスコート予約管理", page_icon="🎾", layout="centered")

# カラースタイル（ミント×オレンジ×白）
st.markdown("""
    <style>
        body {
            background-color: #fafffa;
        }
        .main-title {
            font-size: 30px;
            color: #1abc9c;
            text-align: center;
            margin-bottom: 10px;
        }
        .sub-title {
            color: #ff7f50;
            text-align: center;
            margin-bottom: 30px;
        }
        .stButton>button {
            background-color: #1abc9c;
            color: white;
            border-radius: 10px;
            border: none;
            padding: 8px 20px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #16a085;
        }
        table {
            border-radius: 10px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎾 テニスコート予約管理 🎾</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">抽選・確保状況をみんなで楽しく共有しよう！</div>', unsafe_allow_html=True)

# セッション状態でデータを保持
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["施設名", "日付", "時間帯", "担当者", "状態"])

# 入力フォーム
with st.expander("＋ 新しい予約を追加"):
    with st.form("new_entry"):
        col1, col2 = st.columns(2)
        facility = col1.selectbox("施設名", ["けやきねっと", "都営スポーツ施設", "その他"])
        date = col2.date_input("日付")
        time = st.selectbox("時間帯", ["午前", "午後", "夜間"])
        person = st.text_input("担当者（ニックネーム）")
        status = st.radio("状態", ["確保", "抽選中", "中止"], horizontal=True)
        submitted = st.form_submit_button("登録")

        if submitted:
            new_row = {"施設名": facility, "日付": date, "時間帯": time, "担当者": person, "状態": status}
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("✅ 登録しました！")

# データ表示
st.markdown("### 📋 登録一覧")
if len(st.session_state.data) > 0:
    st.dataframe(st.session_state.data, use_container_width=True)
else:
    st.info("まだ登録がありません。上のフォームから追加してください。")

# データ削除
if len(st.session_state.data) > 0:
    st.markdown("---")
    st.markdown("### 🗑️ データ削除")
    del_index = st.number_input("削除したい行番号（0から）", min_value=0, max_value=len(st.session_state.data)-1, step=1)
    if st.button("削除"):
        st.session_state.data = st.session_state.data.drop(del_index).reset_index(drop=True)
        st.success("削除しました！")
