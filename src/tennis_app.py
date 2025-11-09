# src/tennis_app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, time, timedelta
from streamlit_calendar import calendar

# ===== CSVパス =====
CSV_PATH = "../data/reservations.csv"

# ===== データフォルダ・CSV初期化 =====
if not os.path.exists("../data"):
    os.makedirs("../data")

if not os.path.exists(CSV_PATH):
    df_init = pd.DataFrame(columns=[
        "date","facility","status","start_hour","start_minute",
        "end_hour","end_minute","participants","absent"
    ])
    df_init.to_csv(CSV_PATH, index=False)

# ===== CSV読み書き関数 =====
def load_reservations():
    df = pd.read_csv(CSV_PATH)
    # 日付列を安全に変換（失敗はNaT）
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    # participants/absent をリスト化（空文字 -> []）
    def to_list_field(x):
        if pd.isna(x) or x == "":
            return []
        if isinstance(x, list):
            return x
        # 保存は semicolon 区切り
        return str(x).split(";") if ";" in str(x) else eval(str(x)) if str(x).startswith("[") else [s for s in str(x).split(";") if s]
    df["participants"] = df["participants"].apply(to_list_field)
    df["absent"] = df["absent"].apply(to_list_field)
    return df

def save_reservations(df):
    df_to_save = df.copy()
    # date -> YYYY-MM-DD
    df_to_save["date"] = df_to_save["date"].apply(lambda d: d.strftime("%Y-%m-%d") if (not pd.isna(d) and isinstance(d, (date, datetime))) else "")
    # list -> semicolon string
    df_to_save["participants"] = df_to_save["participants"].apply(lambda lst: ";".join(lst) if isinstance(lst, (list, tuple)) else (str(lst) if pd.notna(lst) else ""))
    df_to_save["absent"] = df_to_save["absent"].apply(lambda lst: ";".join(lst) if isinstance(lst, (list, tuple)) else (str(lst) if pd.notna(lst) else ""))
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

# ===== イベント生成 (カレンダー用) =====
events = []
for idx, r in df_res.reset_index().iterrows():
    # idx は DataFrame の reset_index で作った行番号（安全に参照できる）
    # r["date"] は datetime.date か NaT
    if pd.isna(r["date"]):
        continue
    # 可能なら時刻情報を付与した ISO を作る（FullCalendar が解釈できる形式）
    try:
        if pd.notna(r.get("start_hour")) and pd.notna(r.get("start_minute")):
            start_dt = datetime.combine(r["date"], time(int(r["start_hour"]), int(r["start_minute"])))
            end_dt = datetime.combine(r["date"], time(int(r["end_hour"]), int(r["end_minute"]))) if pd.notna(r.get("end_hour")) else (start_dt + timedelta(hours=1))
            start_str = start_dt.isoformat()
            end_str = end_dt.isoformat()
        else:
            start_str = r["date"].strftime("%Y-%m-%d")
            end_str = (r["date"] + timedelta(days=1)).strftime("%Y-%m-%d")
    except Exception:
        # フォールバック：日付のみ
        start_str = r["date"].strftime("%Y-%m-%d")
        end_str = (r["date"] + timedelta(days=1)).strftime("%Y-%m-%d")

    title_str = f"{r.get('status','')} 〇{len(r.get('participants') or [])} ×{len(r.get('absent') or [])}"
    color = status_color.get(r.get("status"), {"bg":"#FFFFFF","text":"black"})
    events.append({
        "id": int(r["index"]),   # reset_index の index を id に使う（元DFのindexを参照）
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
    # ---------- dateClick ----------
    if callback == "dateClick":
        raw_clicked = cal_state["dateClick"]["date"]
        # ISO形式などを安全にパース（例: "2025-11-07T00:00:00.000Z"）
        clicked_date = pd.to_datetime(raw_clicked, utc=True).date()
        st.info(f"📅 {clicked_date} の予約を確認/登録")

        facility = st.text_input("施設名", key=f"facility_{raw_clicked}")

        # 時刻プルダウン（時・分）
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            start_hour = st.selectbox("開始時（時）", list(range(0,24)), key=f"sh_{raw_clicked}")
        with col2:
            start_minute = st.selectbox("開始分", [0,10,20,30,40,50], key=f"sm_{raw_clicked}")
        with col3:
            end_hour = st.selectbox("終了時（時）", list(range(0,24)), key=f"eh_{raw_clicked}")
        with col4:
            end_minute = st.selectbox("終了分", [0,10,20,30,40,50], key=f"em_{raw_clicked}")

        # 見やすく HH:MM 表示
        start_time_str = f"{int(start_hour):02d}:{int(start_minute):02d}"
        end_time_str = f"{int(end_hour):02d}:{int(end_minute):02d}"
        st.markdown(f"**開始:** `{start_time_str}`  **/**  **終了:** `{end_time_str}`")

        status = st.selectbox("ステータス", ["確保","抽選中","中止"], key=f"st_{raw_clicked}")

        if st.button("登録", key=f"reg_{raw_clicked}"):
            # 新規行追加（participants/absent は空リスト）
            new_row = {
                "date": clicked_date,
                "facility": facility,
                "status": status,
                "start_hour": int(start_hour),
                "start_minute": int(start_minute),
                "end_hour": int(end_hour),
                "end_minute": int(end_minute),
                "participants": [],
                "absent": []
            }
            df_res = pd.concat([df_res, pd.DataFrame([new_row])], ignore_index=True)
            save_reservations(df_res)
            st.success(f"{clicked_date} に {facility} を登録しました")
            st.experimental_rerun()

    # ---------- eventClick ----------
    elif callback == "eventClick":
        ev = cal_state["eventClick"]["event"]
        # ev['id'] は reset_index の index（int）を想定
        try:
            idx = int(ev.get("id"))
        except Exception:
            st.error("イベントIDが不正です")
            idx = None

        if idx is not None:
            # 安全に行取得（元の df_res の index と一致するはず）
            try:
                r = df_res.loc[idx]
            except Exception:
                st.error("選択した予約が見つかりません")
                r = None

            if r is not None:
                st.info(f"イベント選択：{r['facility']} ({r.get('status','')})")
                nick = st.text_input("ニックネーム", key=f"nick_{idx}")
                part = st.radio("参加状況", ["参加","不参加"], key=f"part_{idx}")

                if st.button("反映", key=f"apply_{idx}"):
                    # participants/absent はリスト。取得して更新、保存
                    participants = list(r["participants"]) if isinstance(r["participants"], list) else []
                    absent = list(r["absent"]) if isinstance(r["absent"], list) else []

                    # 既存の同名は先に削除
                    if nick in participants:
                        participants.remove(nick)
                    if nick in absent:
                        absent.remove(nick)

                    if part == "参加":
                        participants.append(nick)
                    else:
                        absent.append(nick)

                    # DataFrame に安全に格納（at を使う）
                    df_res.at[idx, "participants"] = participants
                    df_res.at[idx, "absent"] = absent

                    save_reservations(df_res)
                    st.success(f"{nick} は {part} に設定されました")
                    st.experimental_rerun()
