# results_record_db

## 概要

本テーマは、**複数の設備機器から異なるフォームで出力される実績データ**を、
共通ルールで正規化して PostgreSQL に取り込み、
最終的に Streamlit で KPI を可視化するための設計見本である。

今回の題材では、現場でよくある

- 工程ごとに利用ツールが異なる
- ログの列名や時刻表現が揃っていない
- そのままでは KPI 評価に使えない

という状況を模している。

---

## 今回の業務モデル

- 1製番を1台の個体識別単位とし、各工程の作業完了ごとに1レコード記録する
- 製品は 1個流し
- 工程は固定で3つ
  - 内部組立
  - 外部組立
  - 出荷検査
- 1製番あたり最大3件の実績レコードが登録される
- 生産工程は直線ラインで `内部組立 → 外部組立 → 出荷検査`
- 意図的に、それぞれが異なるログフォーマットを持つようにする
- データ期間は `2026-01-05` から `2026-01-30` まで
- 土日と `2026-01-12` の祝日は休業とし、1月の営業日は19日
- 生産は1直で、工程稼働時間は `08:00-17:00`
- `12:00-13:00` は休憩時間とする
- モデル簡略化のため、残業はないものとする

---

## 最終的な評価KPI

本テーマで最終的に評価する KPI は次の3点とする。

1. 工程別時間別の作業台数実績
2. 工程間の滞留状態（15分毎データ）
3. 作業者ごとの日別作業台数

---

## 設計方針

### 1. 記録単位

データベースへの登録単位は **1作業記録1レコード** とする。

- 1製番 = 1台
- 各工程の作業完了ごとに1レコード
- したがって、1製番あたり最大3レコード

### 2. ログ統合の考え方

内部組立、外部組立、出荷検査はそれぞれ別ツールで管理されているため、
元ログの出力フォーマットは異なる。

しかし KPI 評価のためには、工程差・ツール差を吸収し、
**1つの正規化済み実績テーブル** に集約する必要がある。

### 3. 時間項目の扱い

- `start_ts` / `end_ts` は元ログに基づく事実として保持する
- `elapsed_sec` は単純な `end_ts - start_ts` 差分秒
- `work_sec` は、稼働カレンダーに基づいて昼休み・非稼働時間を除いた正味作業時間秒とする

`work_sec` は取込時に計算して保持することで、
後続の集計処理や可視化を簡素化する。

---

## 取込対象テーブル

### テーブル名
`work_log`

### カラム定義

| 物理名 | 論理名 |
|---|---|
| `work_log_id` | 処理シーケンスNo. |
| `order_no` | 受注No.（1台を識別する業務キー） |
| `product_name` | 製品名 |
| `process_name` | 工程名 |
| `worker_name` | 作業者名 |
| `start_ts` | 開始時間 (`YYYY-MM-DD hh:mm:ss`) |
| `end_ts` | 終了時間 (`YYYY-MM-DD hh:mm:ss`) |
| `elapsed_sec` | 純粋な `end_ts - start_ts` 差分秒 |
| `work_sec` | 稼働カレンダーに基づいて昼休み・非稼働時間を除いた正味作業時間秒 |
| `result_cd` | 作業結果（`OK / NG` のいずれか） |
| `source_system` | 入力元種別（`internal_assembly_tool / external_assembly_tool / shipping_inspection_tool` のいずれか） |
| `source_file_name` | ファイル名 |
| `source_row_no` | 行数 |
| `ingest_batch_id` | 取込実行ID |
| `created_at` | 取込時間 (`YYYY-MM-DD hh:mm:ss`) |

---

## PostgreSQL の型定義

| 物理名 | 型 |
|---|---|
| `work_log_id` | `BIGSERIAL` |
| `order_no` | `VARCHAR(30)` |
| `product_name` | `VARCHAR(100)` |
| `process_name` | `VARCHAR(30)` |
| `worker_name` | `VARCHAR(50)` |
| `start_ts` | `TIMESTAMP` |
| `end_ts` | `TIMESTAMP` |
| `elapsed_sec` | `INTEGER` |
| `work_sec` | `INTEGER` |
| `result_cd` | `VARCHAR(10)` |
| `source_system` | `VARCHAR(50)` |
| `source_file_name` | `VARCHAR(255)` |
| `source_row_no` | `INTEGER` |
| `ingest_batch_id` | `VARCHAR(30)` |
| `created_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

---

## 制約の初期案

```sql
PRIMARY KEY (work_log_id)
UNIQUE (order_no, process_name)
