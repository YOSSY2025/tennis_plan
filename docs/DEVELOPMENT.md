# 🧭 DEVELOPMENT.md

**テニスコート予約管理アプリ — 開発手順書（v1.0）**

---

## ■ 開発環境構築手順

| 項目           | 内容                                |
| -------------- | ----------------------------------- |
| 言語           | Python 3.x                          |
| フレームワーク | Streamlit                           |
| 主ライブラリ   | pandas, datetime, uuid              |
| データ保存     | CSV（UTF-8, カンマ区切り）          |
| 実行方法       | `streamlit run src/tennis_app.py` |
| 開発環境       | GitHub + Streamlit Cloud            |

---

## ■ ディレクトリ構成（再掲）

project_root/

├─ docs/

│   ├─ SPECIFICATION.md

│   ├─ BACKLOG.md

│   ├─ DATA_SPEC.md

│   ├─ DEVELOPMENT.md

│   ├─ UI_FLOW.md

│   └─ DOCUMENTS.md

├─ src/

│   └─ tennis_app.py

├─ data/

│   └─ reservations.csv

├─ tests/

└─ README.md

## ■ アプリ構成概要

| モジュール           | 役割         | 主な関数・処理                     |
| -------------------- | ------------ | ---------------------------------- |
| `tennis_app.py`    | メインアプリ | 画面制御・状態管理・CSV入出力      |
| `reservations.csv` | データ保持   | アプリ起動時にロード／更新時に保存 |

## ■ データ処理フロー

| フェーズ          | 処理内容                               | 実装方法（想定）                                    |
| ----------------- | -------------------------------------- | --------------------------------------------------- |
| 1. 起動時         | `reservations.csv` 読み込み          | `pandas.read_csv()`                               |
| 2. カレンダー表示 | 日付別にデータを整形し表示             | groupby(date)                                       |
| 3. 登録・編集     | フォーム入力をDataFrameに追加／更新    | `df.append()` または `df.loc[]`                 |
| 4. 削除           | 対象ID行を削除                         | `df.drop()`                                       |
| 5. 自動完了化     | 今日の日付より前の予約を完了扱いに変更 | `if date < today: status = "完了"`                |
| 6. 保存           | DataFrameをCSVに書き戻し               | `df.to_csv("data/reservations.csv", index=False)` |

---

## ■ UIイベント設計（概要）

| イベント               | 動作                       | 備考             |
| ---------------------- | -------------------------- | ---------------- |
| カレンダー日付クリック | 該当日の詳細モーダルを開く | 新規／編集両対応 |
| 予約登録ボタン押下     | CSVへ追記・保存            | UUID発行         |
| 削除ボタン押下         | 確認ダイアログ表示後に削除 | 誤操作防止       |
| ステータス更新         | 日次チェックで自動実行     | 起動時にも反映   |
| 参加表明入力           | 該当予約に紐づけて人数更新 | 参加〇・不参加× |

---

## ■ 今後の拡張予定（次フェーズ対応）

| 優先度 | 機能                | 概要                                      |
| :----: | ------------------- | ----------------------------------------- |
| ★★★ | 抽選期間管理        | 別CSV（lottery_period.csv）による期間表示 |
| ★★☆ | バックアップ機能    | 定期的にCSVを自動保存                     |
| ★☆☆ | Google Calendar API | 外部連携機能（v3以降）                    |

---

## ■ 開発フロー（運用手順）

1. ブランチ作成（例：`feature/calendar-ui`）
2. 機能単位でコミット
3. 動作確認後、`main` にマージ
4. Streamlit Cloudでデプロイ確認
5. GitHubでドキュメント更新



## 🔧 GoogleサービスアカウントJSONファイルの取得・保存手順

| ステップ | 操作内容                                                                     | 備考                                     |
| -------- | ---------------------------------------------------------------------------- | ---------------------------------------- |
| ①       | [Google Cloud Console](https://console.cloud.google.com/)にログイン             | 同じGoogleアカウントで                   |
| ②       | 上部のプロジェクト選択で、対象プロジェクトを開く                             | スプレッドシートを操作したいプロジェクト |
| ③       | 左のメニューで**「IAMと管理」→「サービスアカウント」**を開く                |                                          |
| ④       | 右上の**「＋サービスアカウントを作成」**をクリック                           |                                          |
| ⑤       | 任意の名前を入力 → 「作成して続行」                                         | 例：`streamlit-access`                 |
| ⑥       | ロールを追加 → 「プロジェクト」→「編集者」または「スプレッドシート編集者」 | 後から調整可                             |
| ⑦       | 「完了」→ 一覧に新しいアカウントが追加される                                |                                          |
| ⑧       | そのアカウントの右側「︙」→**「鍵を管理」**をクリック                       |                                          |
| ⑨       | 「鍵を追加」→**「新しい鍵を作成」→「JSON」**を選択                         | 自動的にダウンロードされる               |
| ⑩       | ダウンロードされたファイルを、プロジェクト内に保存                           | 例：`src/service_account.json`         |

---

## 📁 保存例（あなたのプロジェクト構成）

<pre class="overflow-visible!" data-start="710" data-end="834"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>tennis_plan/
├─ </span><span>src</span><span>/
│   ├─ tennis_app</span><span>.py</span><span>
│   ├─ service_account</span><span>.json</span><span>  ←★ ここに置く
│
└─ </span><span>.streamlit</span><span>/
    └─ secrets</span><span>.toml</span><span>
</span></span></code></div></div></pre>

---

## 🧩 secrets.toml の記述例

<pre class="overflow-visible!" data-start="866" data-end="963"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-toml"><span><span>[google]</span><span>
</span><span>service_account_file</span><span> = </span><span>"src/service_account.json"</span><span>
</span><span>sheet_id</span><span> = </span><span>"ここにスプレッドシートID"</span><span>
</span></span></code></div></div></pre>

---

## 🧠 Python側（tennis_app.py）

<pre class="overflow-visible!" data-start="1000" data-end="1398"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>import</span><span> streamlit </span><span>as</span><span> st
</span><span>from</span><span> google.oauth2 </span><span>import</span><span> service_account
</span><span>import</span><span> gspread

</span><span># 認証</span><span>
service_account_file = st.secrets[</span><span>"google"</span><span>][</span><span>"service_account_file"</span><span>]
creds = service_account.Credentials.from_service_account_file(service_account_file)
client = gspread.authorize(creds)

</span><span># スプレッドシート接続</span><span>
sheet = client.open_by_key(st.secrets[</span><span>"google"</span><span>][</span><span>"sheet_id"</span><span>])
worksheet = sheet.sheet1  </span><span># 例：1枚目のシート</span><span>
</span></span></code></div></div></pre>

---

この構成なら、**ローカル実行でも Streamlit Cloud でも動作します。**

（Streamlit Cloud にデプロイする際は、同じJSONファイルを `.streamlit/secrets.toml` にアップロードして指定するだけ）

---

（最終更新：2025年11月）
