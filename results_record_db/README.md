# results_record_db

## 概要

本テーマは、**複数の設備機器から異なるフォームで出力される実績データ**を、
共通ルールで正規化して PostgreSQL に取り込み、
最終的に Streamlit で KPI を可視化するための設計見本である。

今回の題材では、現場でよくある

- 工程ごとに利用ツールが異なる = ログのフォーマットが異なる
- ログの列名や時刻表現、粒度が揃っていない
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
- 意図的に誤った作業ログデータを設けてDBレコード登録処理の段階で除外する ※

※ kpiテーブルの正しさを求めることが目的なので、不正な値をフラグ付きで取り込んだ場合、除外漏れなどの懸念がある

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

### 4. 値の固定方針

本テーマでは、集計と説明を簡潔にするため、
一部の値は自由入力とせず、あらかじめ許容値を固定する。

#### `process_name`
- `内部組立`
- `外部組立`
- `出荷検査`

#### `result_cd`
- `OK`
- `NG`

#### `source_system`
- `internal_assembly_tool`
- `external_assembly_tool`
- `shipping_inspection_tool`

### 5. 作業者名の扱い

本テーマでは `worker_name` をそのまま保持する。  
実務では `worker_id` の方が安全であるが、今回はセミナー題材のため、
**まずは作業者名で可視化・集計できること** を優先する。

ただし、元ログ側の表記ゆれは取込時に吸収する前提とする。

例:
- `山田太郎`
- `山田　太郎`
- `Yamada Taro`

のような揺れは、正規化時に統一する。

---

## 主テーブル

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
| `source_system` | 入力元種別 |
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

## NOT NULL 方針

本テーマでは、主テーブルの主要列には強めに `NOT NULL` を付与する。

対象列は以下を想定する。

- `order_no`
- `product_name`
- `process_name`
- `worker_name`
- `start_ts`
- `end_ts`
- `elapsed_sec`
- `work_sec`
- `result_cd`
- `source_system`
- `source_file_name`
- `source_row_no`
- `ingest_batch_id`

`work_log_id` は主キーのため `NOT NULL` 相当、
`created_at` は `DEFAULT CURRENT_TIMESTAMP` により必須値を持つ前提とする。

---

## 制約の初期案

### 主キー・一意制約

```sql
PRIMARY KEY (work_log_id)
UNIQUE (order_no, process_name)
```

本テーマでは、

- 1製番 = 1台
- 各工程は1回だけ記録
- `result_cd` は `OK / NG` のみ

という前提のため、`UNIQUE (order_no, process_name)` を採用する。

### CHECK 制約

```sql
CHECK (process_name IN ('内部組立', '外部組立', '出荷検査'))
CHECK (result_cd IN ('OK', 'NG'))
CHECK (source_system IN (
  'internal_assembly_tool',
  'external_assembly_tool',
  'shipping_inspection_tool'
))
CHECK (end_ts >= start_ts)
CHECK (elapsed_sec >= 0)
CHECK (work_sec >= 0 AND work_sec <= elapsed_sec)
```

---

## reject テーブル

主テーブルに登録できなかった行については、
**別テーブルに reject 理由付きで記録する** 方針とする。

### テーブル名
`work_log_reject`

### カラム定義

| 物理名 | 論理名 |
|---|---|
| `reject_id` | rejectシーケンスNo. |
| `source_system` | 入力元種別 |
| `source_file_name` | ファイル名 |
| `source_row_no` | 行数 |
| `reject_reason_cd` | reject理由コード |
| `reject_reason_detail` | reject理由詳細 |
| `raw_payload_json` | 元行データ |
| `ingest_batch_id` | 取込実行ID |
| `created_at` | reject記録時間 |

### reject テーブルの目的

- 取込できなかった行を捨てっぱなしにしない
- どの入力元のどの行が問題だったかを追跡できる
- KPI に載らなかった理由を説明できる

### reject 理由の例

- 必須列欠損
- 日付変換失敗
- `end_ts < start_ts`
- `elapsed_sec < 0`
- `work_sec < 0`
- `process_name` 不正
- `result_cd` 不正
- 一意制約違反（重複）

---

## ingest_batch_id の生成ルール

`ingest_batch_id` は **1回の取込実行単位を識別するID** とする。

生成ルールは簡易な文字列ルールでよい。

例:

```text
ING_YYYYMMDD_HH24MISS_連番
```

具体例:

```text
ING_20260105_081530_001
```

この形式とすることで、

- 同じファイルを再取込した場合でも別実行として識別できる
- 主テーブルと reject テーブルを batch 単位で追跡できる
- セミナーで意味を説明しやすい

---

## インデックス方針

最終KPIを効率よく集計するため、初期段階から最低限のインデックスを意識する。

### 推奨インデックス

```sql
CREATE INDEX idx_work_log_process_end_ts ON work_log (process_name, end_ts);
CREATE INDEX idx_work_log_worker_end_ts  ON work_log (worker_name, end_ts);
CREATE INDEX idx_work_log_order_process  ON work_log (order_no, process_name);
```

### 目的

- `process_name + end_ts`
  - 工程別時間別の作業台数実績
- `worker_name + end_ts`
  - 作業者ごとの日別作業台数
- `order_no + process_name`
  - 工程間滞留判定
  - 工程別進捗確認

---

## 補足ルール

### `work_sec` の考え方

`work_sec` は以下を除外した正味作業時間とする。

- 昼休み `12:00-13:00`
- 非稼働時間帯（`08:00` より前、`17:00` より後）

### 稼働カレンダー前提

- 稼働日: `2026-01-05` ～ `2026-01-30` のうち、土日と `2026-01-12` を除く日
- 1月営業日数: 19日
- 稼働時間: `08:00-17:00`
- 休憩時間: `12:00-13:00`
- 残業: なし

---

## このテーマで扱う課題

本テーマで解決すべき課題は、単に CSV を読み込むことではない。

- 異なるログフォーマットを共通カラムへマッピングすること
- 同じ意味のデータを同じ定義で扱えるようにすること
- KPI に不要な揺れや曖昧さを取込時点で吸収すること
- 不正行や重複行を reject として明示的に扱うこと
- Streamlit で見せたい分析指標へつながる形で DB 設計すること

---

## この後に設計するもの

- 工程別の元ログフォーマット定義
  - 内部組立ログ
  - 外部組立ログ
  - 出荷検査ログ
- 元ログから `work_log` へのマッピング定義
- reject 条件定義
- PostgreSQL DDL
- Streamlit での KPI 可視化要件

---

## ゴール

最終的には、異なる設備ログを取り込み、正規化済みテーブル `work_log` を元に、

- 工程別時間別の作業台数
- 工程間滞留
- 作業者別日次実績

を Streamlit 上で確認できる状態を目指す。

---

---
# 取り込む予定の実績ログデータの設計指針

## フォーマット
  - 内部組立ログ
  - 外部組立ログ
  - 出荷検査ログ
の3種をそれぞれ異なるフォーマットとする。また、取り込む必要のないカラムなども設定する。具体的にはこれから検討をおこなう。

## 不正データの扱い

本テーマでは、**不正データは主テーブル `work_log` には取り込まず、取込時に除外して reject テーブルへ記録する** 方針とする。

理由は以下のとおりである。

- `work_log` を KPI 集計専用の正規データに保ちたい
- 集計SQLや可視化画面で毎回 `error_flag = 0` のような条件を要求しないようにしたい
- 不正データを残す場合でも、主テーブルではなく reject 側で理由付き管理した方が追跡しやすい
- `NOT NULL` や `CHECK` 制約を素直に強く掛けられる

したがって、取込結果は次の2系統に分かれる。

- 正常データ: `work_log` に登録する
- 不正データ: `work_log_reject` に登録する

---

## reject テーブルの位置付け

`work_log_reject` は、単に「捨てたデータ」を置く場所ではない。  
**どのファイルのどの行が、なぜ主テーブルへ取り込まれなかったのか** を残すための監査・再確認用テーブルである。

このため、reject テーブルには少なくとも以下を記録する。

- 入力元種別
- ファイル名
- 行番号
- reject 理由コード
- reject 理由詳細
- 元行データ
- 取込実行ID
- reject 記録時間

これにより、

- KPI に含まれなかった理由を説明できる
- 元ファイルの修正対象を追跡できる
- 同一バッチの取込結果をまとめて確認できる

---

## 入力不正と業務異常の切り分け

本テーマでは、**入力不正** と **業務異常** を分けて扱う。

### 入力不正
入力形式や値として成立しておらず、主テーブルへ登録してはいけないもの。  
これらは reject 対象とする。

例:
- 必須列欠損
- 日付変換失敗
- `end_ts < start_ts`
- `elapsed_sec < 0`
- `work_sec < 0`
- `work_sec > elapsed_sec`
- `process_name` が未定義値
- `result_cd` が未定義値
- `source_system` が未定義値
- `UNIQUE (order_no, process_name)` に抵触する重複データ

### 業務異常
形式上は正しく、主テーブルへ登録可能だが、現場改善や分析上は注意が必要なもの。  
これらは reject せず、`work_log` に登録したうえで KPI や個別分析で扱う。

例:
- 作業時間が極端に長い
- 作業時間が極端に短い
- 特定工程だけ NG が多い
- 同一作業者に負荷が偏っている
- 工程間滞留が偏在している

---

## サンプルデータに意図的に含める誤り

セミナー用のサンプルデータには、正常データだけでなく、実務で起こりやすい誤りを意図的に混ぜる。

### 必ず含めたい誤り
- 同じデータを2回取り込むケース
- 必須列欠損
- 日付変換失敗
- `end_ts < start_ts`
- `elapsed_sec < 0`
- `work_sec < 0`
- `work_sec > elapsed_sec`
- `process_name` の誤記
- `result_cd` の誤記
- 列ズレ / 桁ズレにより値が想定列へ入っていないケース

### 二重取込の扱い
同じファイルを2回取り込んでも、`work_log` の件数は増加しないことを確認する。  
これにより、一意制約と重複排除処理が正しく機能していることを示す。

---

## 取込処理の設計方針

本テーマでは、取込処理は **入口と中核ロジックを分離** する方針とする。

### 入口
- CLI: 定時バッチや大量処理向け
- Web / Streamlit: 手動アップロード、エラー確認、例外対応向け

### 中核
- `ingest_core` に変換・検証・登録ロジックを集約する

この構成により、

- 入口が違っても同じ判定基準で取り込める
- 仕様変更時の修正箇所を一箇所に集約できる
- 製造業でありがちな「定時自動取込」と「手動再取込」を同じルールで扱える

---

## 推奨する取込フロー

1. ファイル受領
2. `source_system` 判定
3. 元フォーマットごとの列名マッピング
4. 型変換
5. 必須チェック
6. 値域チェック
7. `elapsed_sec` / `work_sec` 計算
8. 正常データと reject データへ振り分け
9. 取込実行IDを付与
10. `work_log` へ登録
11. `work_log_reject` へ登録
12. 取込サマリを記録・表示

---

## 取込実行単位の記録

`ingest_batch_id` は、1回の取込実行を識別するためのIDである。  
主テーブルと reject テーブルの両方に保持することで、同一取込の結果をまとめて追跡できるようにする。

形式は簡易な文字列ルールで十分とする。

例:

```text
ING_20260105_081530_001
