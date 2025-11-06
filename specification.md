
# テニスコート予約管理アプリ 仕様書（v1.0）

---

## ■ 概要

本アプリは、複数人で行うテニスコートの「抽選・予約」情報を共有・管理するためのWebアプリケーションです。

主にスマートフォンから操作しやすいUIを想定し、月単位のカレンダーで直感的に予約状況を確認できます。

---

## ■ 目的

* 誰が・どこの施設を・いつ予約／抽選しているかを全員が把握できる
* 抽選申し込み期間や確保状況を忘れずに管理
* LINEやスプレッドシートでは管理しにくい情報を、見やすいUIで一元化

---

## ■ 画面構成

| 画面名           | 概要                                                         |
| ---------------- | ------------------------------------------------------------ |
| トップ画面       | 月カレンダー表示。予約状況（ステータス・参加人数）を確認     |
| 予約詳細モーダル | 予約登録・編集・削除、確認ダイアログ付き                     |
| 参加表明画面     | 確保予約に対して参加／不参加表明。参加人数・不参加人数を表示 |
| 抽選期間確認画面 | 複数抽選の申込期間・利用期間を表示。申込中の抽選は登録可能   |

---

## ■ データ構造

### 1. reservations

| 列名           | 型       | 説明                           |
| -------------- | -------- | ------------------------------ |
| reservation_id | int      | 予約ID（自動生成）             |
| date           | date     | 利用日                         |
| start_time     | time     | 開始時間（10分単位プルダウン） |
| end_time       | time     | 終了時間（10分単位プルダウン） |
| facility_name  | string   | 施設名（直接入力）             |
| status         | string   | 確保・抽選中・中止・完了       |
| organizer      | string   | 担当者ニックネーム             |
| lottery_id     | int/null | 紐づく抽選ID（任意）           |

### 2. participation_status

| 列名           | 型     | 説明                     |
| -------------- | ------ | ------------------------ |
| reservation_id | int    | 紐づく予約ID             |
| participant    | string | 参加者ニックネーム       |
| participation  | string | 〇（参加）／×（不参加） |

### 3. lottery_periods

| 列名          | 型     | 説明               |
| ------------- | ------ | ------------------ |
| lottery_id    | int    | 抽選ID（自動生成） |
| lottery_type  | string | 抽選区分           |
| facility_name | string | 対象施設           |
| apply_start   | date   | 申込開始日         |
| apply_end     | date   | 申込終了日         |
| usage_start   | date   | 利用開始日         |
| usage_end     | date   | 利用終了日         |
| status        | string | 申込中／締切済     |

---

## ■ 予約ステータス

| ステータス | 色    | 説明               |
| ---------- | ----- | ------------------ |
| 確保       | 🟩 緑 | 予約確定           |
| 抽選中     | 🟨 黄 | 抽選応募中         |
| 中止       | ⬜ 灰 | 予約中止           |
| 完了       | ⬜ 灰 | 利用日が過ぎた予約 |

---

## ■ UIデザイン方針

| 要素           | 内容                           |
| -------------- | ------------------------------ |
| カラーイメージ | ミント × オレンジ × 白       |
| タイトル       | 「テニスコート予約管理」       |
| フォント       | 柔らかく読みやすい丸ゴシック系 |
| 雰囲気         | 明るく・楽しく・ポップ         |
| レイアウト     | 月カレンダー中心、カード風     |

---

## ■ 機能一覧

| 優先度 | 機能名                       | 概要                                       | 実装タイミング |
| ------ | ---------------------------- | ------------------------------------------ | -------------- |
| ★★★ | 予約登録・編集・削除         | カレンダー日付をタップして登録・編集・削除 | v1.0           |
| ★★★ | 参加表明                     | 予約に対して参加／不参加表明、人数集計表示 | v1.0           |
| ★★☆ | 抽選期間表示                 | 抽選期間・抽選状況をカード表示             | v1.1           |
| ★☆☆ | 抽選申し込み期間リマインダー | 締切前に通知（メール or 画面上）           | v2.0           |
| ★☆☆ | CSV自動バックアップ          | 定期的に保存                               | v2.3           |

---

## ■ 開発・運用環境

| 項目           | 内容                                 |
| -------------- | ------------------------------------ |
| 開発言語       | Python 3.x                           |
| フレームワーク | Streamlit                            |
| デプロイ環境   | Streamlit Cloud                      |
| バージョン管理 | GitHub（Public Repository）          |
| 主なライブラリ | pandas, datetime, streamlit-calendar |
| デバイス対応   | スマホ縦画面メイン、PCサブ           |

---

## ■ 画面遷移フロー（簡易）

<pre class="overflow-visible!" data-start="4070" data-end="4138"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>トップ画面（月カレンダー）
 ├─ 予約詳細モーダル（登録／編集／削除）
 ├─ 参加表明画面
 └─ 抽選期間確認画面
</span></span></code></div></div></pre>

---

## ■ 今後の開発フロー

1. この仕様書を `SPECIFICATION.md` として GitHub に保存
2. データ管理クラス（ReservationManager / ParticipationManager / LotteryManager）作成
3. トップ画面カレンダー実装
4. 予約モーダル・参加表明画面実装
5. 抽選期間確認画面実装
6. フィードバック反映・v1.1更新
7. 将来的な拡張（バックログ）を v2.0 以降で実装

---

（最終更新日：2025年11月）

---
