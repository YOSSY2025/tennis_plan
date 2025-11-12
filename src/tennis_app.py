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
        "end_hour","end_minute","participants","absent","message"
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
    if "message" not in df.columns:
        df["message"] = ""
    df["message"] = df["message"].fillna("")
    return df

def save_reservations(df):
    df_to_save = df.copy()
    df_to_save["date"] = df_to_save["date"].apply(lambda d: d.strftime("%Y-%m-%d") if isinstance(d, (date, datetime)) else "")
    df_to_save["participants"] = df_to_save["participants"].apply(lambda lst: ";".join(lst) if isinstance(lst, list) else "")
    df_to_save["absent"] = df_to_save["absent"].apply(lambda lst: ";".join(lst) if isinstance(lst, list) else "")
    df_to_save["message"] = df_to_save["message"].fillna("")

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


st.markdown("<h3>🎾 テニスコート予約管理</h3>", unsafe_allow_html=True)

# ===== データ読み込み =====
df_res = load_reservations()

# ===== カレンダーイベント生成 =====
events = []
for idx, r in df_res.iterrows():
    if pd.isna(r["date"]):
        continue

    start_dt = datetime.combine(r["date"], time(int(r.get("start_hour",0)), int(r.get("start_minute",0))))
    end_dt   = datetime.combine(r["date"], time(int(r.get("end_hour",0)), int(r.get("end_minute",0))))

    color = status_color.get(r["status"], {"bg":"#FFFFFF","text":"black"})

    # タイトルをステータス＋施設名のみにする
    title_str = f"{r['status']} {r['facility']}"

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
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": ""},
        "eventDisplay": "block",
        "displayEventTime": False,
        "height": "auto",         # ✅ 高さを自動調整（重要）
        "contentHeight": "auto",  # ✅ カレンダー内コンテンツに応じて伸縮
        "aspectRatio": 1.2,       # ✅ 横長になりすぎないよう調整（1.0〜1.5で微調整）
        "titleFormat": {  # ここを追加
            "year": "numeric",
            "month": "2-digit"  # 12 のように2桁で表示
        }
    },
    key="reservation_calendar"
)

# ===== CSSで親要素の高さを自然にする =====
st.markdown("""
<style>
/* Streamlitのコンテナの余白を調整 */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

/* カレンダーの横スクロールを防ぐ */
.fc {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

/* スマホ向けに最適化 */
@media (max-width: 768px) {
    .fc {
        font-size: 0.8rem !important;
    }
    .fc-toolbar-title {
        font-size: 1rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ===== イベント操作 =====
if cal_state:
    callback = cal_state.get("callback")

    # ---- 日付クリック ----
    if callback == "dateClick":
        clicked_date = cal_state["dateClick"]["date"]
        clicked_date_jst = to_jst_date(clicked_date)

        st.session_state['clicked_date'] = clicked_date
        st.session_state['clicked_date_jst'] = clicked_date_jst
    
        # スクロール用のアンカーと自動スクロール
        st.markdown('<div id="form-section"></div>', unsafe_allow_html=True)
        st.markdown("""
        <script>
        document.getElementById('form-section').scrollIntoView({behavior: 'smooth'});
        </script>
        """, unsafe_allow_html=True)
        
        st.info(f"📅 {clicked_date_jst} の予約を確認/登録")

        # ---- 日付クリック時の施設名入力 ----
        # 過去登録済み施設
        past_facilities = df_res['facility'].dropna().unique().tolist()
        facility_select = st.selectbox("施設を選択（新規は入力欄に入力）", options=past_facilities + ["新規"], index=0)

        # 新規の場合だけ入力欄を表示
        if facility_select == "新規":
            facility = st.text_input("施設名を入力")
        else:
            facility = facility_select

        status = st.selectbox("ステータス", ["確保", "抽選中", "中止"], key=f"st_{clicked_date}")

        # --- 時間選択（30分単位 + コンパクト配置 + モバイル調整） ---
        st.markdown("**開始時間**", help="下のスクロールで設定します。")
        st.write("")  # 空行を1つだけ入れて間隔を最小限に
        start_time = st.time_input(
            label="",
            value=time(9, 0),
            key=f"start_{clicked_date}",
            step=timedelta(minutes=30),
            label_visibility="collapsed"
        )

        st.markdown("<div style='margin-top:-10px'></div>", unsafe_allow_html=True)
        st.markdown("**終了時間**")
        st.write("")
        end_time = st.time_input(
            label="",
            value=time(10, 0),
            key=f"end_{clicked_date}",
            step=timedelta(minutes=30),
            label_visibility="collapsed"
        )

        # --- 📝 メッセージ欄を追加 ---
        message = st.text_area(
            "メッセージ（任意）",
            placeholder="例：集合時間や持ち物など",
            key=f"msg_{clicked_date}"
        )


        # --- 登録ボタン ---
        clicked_date = st.session_state.get('clicked_date')
        clicked_date_jst = st.session_state.get('clicked_date_jst')

        if clicked_date is not None:
            if st.button("登録", key=f"reg_{clicked_date}"):
                if end_time <= start_time:
                    st.warning("⚠️ 終了時間は開始時間より後にしてください。")
                else:
                    df_res = pd.concat([df_res, pd.DataFrame([{
                        "date": clicked_date_jst,
                        "facility": facility,
                        "status": status,
                        "start_hour": start_time.hour,
                        "start_minute": start_time.minute,
                        "end_hour": end_time.hour,
                        "end_minute": end_time.minute,
                        "participants": [],
                        "absent": [],
                        "message": message
                    }])], ignore_index=True)
                    save_reservations(df_res)
                    st.success(f"{clicked_date_jst} に {facility} を登録しました")
                    st.experimental_rerun()


# ---- イベントクリック ----
    elif callback == "eventClick":
        ev = cal_state["eventClick"]["event"]
        idx = int(ev["id"])
        
        # スクロール用のアンカーと自動スクロール
        st.markdown('<div id="form-section"></div>', unsafe_allow_html=True)
        st.markdown("""
        <script>
        document.getElementById('form-section').scrollIntoView({behavior: 'smooth'});
        </script>
        """, unsafe_allow_html=True)
        
        if idx not in df_res.index:
            st.warning("このイベントは存在しません。")
        else:
            r = df_res.loc[idx]
            event_date = to_jst_date(r["date"])

            # 詳細表示（改行対応）
            st.markdown(f"""
    ### イベント詳細
    日付: {event_date}<br>
    施設: {r['facility']}<br>
    ステータス: {r['status']}<br>
    時間:<br> &nbsp;&nbsp;{int(r['start_hour']):02d}:{int(r['start_minute']):02d} - {int(r['end_hour']):02d}:{int(r['end_minute']):02d}<br>
    参加者:<br> &nbsp;&nbsp;{', '.join(r['participants']) if r['participants'] else 'なし'}<br>
    不参加者:<br> &nbsp;&nbsp;{', '.join(r['absent']) if r['absent'] else 'なし'}<br>
    メッセージ:<br> &nbsp;&nbsp;{r['message'] if pd.notna(r.get('message')) and r['message'] else '（なし）'}

    """, unsafe_allow_html=True)

            # 施設名選択（過去登録から選択可）
            # 過去登録済み施設
            past_facilities = df_res['facility'].dropna().unique().tolist()
            # ニックネーム選択
            # 過去登録済みニックネーム
            past_nicks = list(set([n for lst in df_res['participants'].tolist() + df_res['absent'].tolist() for n in lst if n]))
            nick_select = st.selectbox("ニックネームを選択（新規は入力欄に）", options=past_nicks + ["新規"], index=0)

            # 新規の場合だけ入力欄を表示
            if nick_select == "新規":
                nick = st.text_input("ニックネームを入力")
            else:
                nick = nick_select

            # 参加状況
            part = st.radio("参加状況", ["参加", "不参加", "削除"], key=f"part_{idx}")

            if st.button("反映", key=f"apply_{idx}"):
                participants = list(r["participants"]) if isinstance(r["participants"], list) else []
                absent = list(r["absent"]) if isinstance(r["absent"], list) else []

                # まず既存から削除
                if nick in participants:
                    participants.remove(nick)
                if nick in absent:
                    absent.remove(nick)

                # 反映
                if part == "参加":
                    participants.append(nick)
                elif part == "不参加":
                    absent.append(nick)
                # 削除は既にリストから削除済み

                df_res.at[idx, "participants"] = participants
                df_res.at[idx, "absent"] = absent
                save_reservations(df_res)
                st.success(f"{nick} は {part} に設定されました")
                st.experimental_rerun()

            # イベント操作
            st.markdown("---")
            st.subheader("イベント操作")
            operation = st.radio(
                "操作を選択",
                ["ステータス変更", "メッセージ変更","削除"],
                key=f"ev_op_{idx}"
            )

            if operation == "ステータス変更":
                new_status = st.selectbox(
                    "新しいステータス",
                    ["確保", "抽選中", "中止", "完了"],
                    key=f"status_change_{idx}"
                )
                if st.button("変更を反映", key=f"apply_status_{idx}"):
                    df_res.at[idx, "status"] = new_status
                    save_reservations(df_res)
                    st.success(f"イベントのステータスを {new_status} に変更しました")
                    st.experimental_rerun()

            elif operation == "削除":
                st.warning("⚠️ このイベントを削除しようとしています。")
                confirm_delete = st.checkbox("本当に削除しますか？", key=f"confirm_del_{idx}")
                if confirm_delete:
                    if st.button("削除を確定", key=f"delete_{idx}"):
                        df_res = df_res.drop(idx).reset_index(drop=True)
                        save_reservations(df_res)
                        st.success("イベントを削除しました")
                        st.experimental_rerun()

            elif operation == "メッセージ変更":
                new_message = st.text_area(
                    "メッセージを入力",
                    value=r.get("message", ""),
                    key=f"message_change_{idx}",
                    height=100
                )
                if st.button("変更を反映", key=f"apply_message_{idx}"):
                    df_res.at[idx, "message"] = new_message
                    save_reservations(df_res)
                    st.success("イベントのメッセージを変更しました")
                    st.experimental_rerun()