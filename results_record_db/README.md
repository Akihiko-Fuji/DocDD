# results_record_db 設計ガイド

## 概要

本ドキュメントは、**複数の設備機器から異なるフォームで出力される実績データ**を、
共通ルールで正規化して PostgreSQL に取り込み、
最終的に Streamlit で KPI を可視化するシステムの **設計・開発ガイド**である。

セミナー題材として、現場でよくある以下の状況を模している。

- 工程ごとに利用ツールが異なる → ログのフォーマットが異なる
- ログの列名・時刻表現・粒度が揃っていない
- そのままでは KPI 評価に使えない

---

## 目次

1. [業務モデル](#1-業務モデル)
2. [最終的な評価 KPI](#2-最終的な評価-kpi)
3. [ゴール](#3-ゴール)
4. [DB 設計](#4-db-設計)
   - 4.1 [主テーブル `work_log`](#41-主テーブル-work_log)
   - 4.2 [reject テーブル `work_log_reject`](#42-reject-テーブル-work_log_reject)
   - 4.3 [制約・インデックス](#43-制約インデックス)
   - 4.4 [`ingest_batch_id` の生成ルール](#44-ingest_batch_id-の生成ルール)
5. [元ログ詳細設計](#5-元ログ詳細設計)
   - 5.1 [内装組立ログ](#51-内装組立ログ文脈補完が必要な設備生ログ)
   - 5.2 [外装組立ログ](#52-外装組立ログ業務列が多い実績ログ)
   - 5.3 [出荷検査ログ](#53-出荷検査ログ判定を丸める検査ログ)
   - 5.4 [3ログ共通の正規化先](#54-3ログ共通の正規化先)
6. [取込処理の設計方針](#6-取込処理の設計方針)
7. [サンプルデータ設計](#7-サンプルデータ設計)
   - 7.1 [サンプル CSV イメージ](#71-サンプル-csv-イメージ)
   - 7.2 [意図的に含める不正データ](#72-意図的に含める不正データ)
   - 7.3 [作成ステップ](#73-作成ステップ)
8. [今後の作業](#8-今後の作業)
9. [実装前提と補足仕様](#9-実装前提と補足仕様)
   - 9.1 [実装前提](#91-実装前提)
   - 9.2 [work_sec 算出の境界条件](#92-work_sec-算出の境界条件)
   - 9.3 [ファイル名からの worker_name 抽出規則](#93-ファイル名からの-worker_name-抽出規則)
   - 9.4 [worker_name 正規化ルール](#94-worker_name-正規化ルール)
   - 9.5 [source_row_no の基点](#95-source_row_no-の基点)
   - 9.6 [duplicate の扱い](#96-duplicate-の扱い)
   - 9.7 [テストの期待値](#97-テストの期待値)
   - 9.8 [Streamlit 画面の最小要件](#98-streamlit-画面の最小要件)
   - 9.9 [実装時の基本姿勢](#99-実装時の基本姿勢)
10. [アーキテクチャ図](#10-アーキテクチャ図)
   - 10.1 [入口と共通ロジックの分離](#101-入口と共通ロジックの分離)
   - 10.2 [本テーマでの実装ファイルとの対応](#102-本テーマでの実装ファイルとの対応)
11. [用語集](#11-用語集)
   - 11.1 [本テーマで特に重要な用語](#111-本テーマで特に重要な用語)


---

## 1. 業務モデル

| 項目 | 内容 |
|---|---|
| 記録単位 | 1製番 = 1台。各工程完了ごとに1レコード |
| 生産方式 | 1個流し |
| 工程 | 内装組立 → 外装組立 → 出荷検査（固定3工程） |
| 最大レコード数 | 1製番あたり3件 |
| データ期間 | 2026-01-05 〜 2026-01-30 |
| 休業日 | 土日 + 2026-01-12（祝日）|
| 営業日数 | 19日 |
| 稼働時間 | 08:00 〜 17:00（1直） |
| 休憩時間 | 12:00 〜 13:00 |
| 残業 | なし |

各工程のログは**異なるフォーマット**で出力される設計とする（題材の肝）。

---

## 2. 最終的な評価 KPI

| # | KPI | 集計軸 |
|---|---|---|
| 1 | 工程別時間別の作業台数実績 | `process_name` × `end_ts`（時間帯） |
| 2 | 工程間の滞留状態 | `order_no` × 工程間の時間差（15分粒度） |
| 3 | 作業者ごとの日別作業台数 | `worker_name` × `end_ts`（日付） |

---

## 3. ゴール

異なる設備ログを取り込み、正規化済みテーブル `work_log` を元に、
以下を Streamlit 上で確認できる状態を作る。

- 工程別時間別の作業台数
- 工程間滞留の可視化
- 作業者別日次実績

**このテーマで解決すべき課題は、単に CSV を読み込むことではない。**

- 異なるログフォーマットを共通カラムへマッピングすること
- 同じ意味のデータを同じ定義で扱えるようにすること
- KPI に不要な揺れや曖昧さを取込時点で吸収すること
- 不正行・重複行を reject として明示的に扱うこと
- Streamlit で見せたい分析指標へつながる形で DB 設計すること

---

## 4. DB 設計

### 4.1 主テーブル `work_log`

#### カラム定義

| 物理名 | 論理名 | 型 | NOT NULL |
|---|---|---|---|
| `work_log_id` | 処理シーケンスNo. | `BIGSERIAL` | PK |
| `order_no` | 受注No.（1台を識別する業務キー） | `VARCHAR(30)` | ○ |
| `product_name` | 製品名 | `VARCHAR(100)` | ○ |
| `process_name` | 工程名 | `VARCHAR(30)` | ○ |
| `worker_name` | 作業者名 | `VARCHAR(50)` | ○ |
| `start_ts` | 開始時間 | `TIMESTAMP` | ○ |
| `end_ts` | 終了時間 | `TIMESTAMP` | ○ |
| `elapsed_sec` | 純粋な `end_ts - start_ts` 差分秒 | `INTEGER` | ○ |
| `work_sec` | 稼働カレンダーに基づく正味作業時間秒 | `INTEGER` | ○ |
| `result_cd` | 作業結果（`OK / NG`） | `VARCHAR(10)` | ○ |
| `source_system` | 入力元種別 | `VARCHAR(50)` | ○ |
| `source_file_name` | ファイル名 | `VARCHAR(255)` | ○ |
| `source_row_no` | 行番号 | `INTEGER` | ○ |
| `ingest_batch_id` | 取込実行ID | `VARCHAR(30)` | ○ |
| `created_at` | 取込時間 | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | DEFAULT |

#### 固定値（許容値）

| カラム | 許容値 |
|---|---|
| `process_name` | `内装組立` / `外装組立` / `出荷検査` |
| `result_cd` | `OK` / `NG` |
| `source_system` | `internal_assembly_tool` / `external_assembly_tool` / `shipping_inspection_tool` |

#### `work_sec` の考え方

`work_sec` は以下を除外した正味作業時間とする。

- 昼休み `12:00-13:00`
- 非稼働時間帯（`08:00` 前、`17:00` 後）

取込時に計算して保持することで、後続の集計・可視化処理を簡素化する。

#### `worker_name` の扱い

本テーマでは `worker_name` をそのまま保持する。
実務では `worker_id` の方が安全だが、セミナー題材のため **作業者名で可視化・集計できること** を優先する。
元ログ側の表記ゆれは取込時に吸収する前提とする。

> 例: `山田太郎` / `山田　太郎` / `Yamada Taro` → 正規化して統一

---

### 4.2 reject テーブル `work_log_reject`

主テーブルに登録できなかった行は、**別テーブルに reject 理由付きで記録する**。
`work_log_reject` は「捨てたデータ置き場」ではなく、**どの行がなぜ取り込まれなかったかを追跡するための監査テーブル**である。

#### カラム定義

| 物理名 | 論理名 | 型 |
|---|---|---|
| `reject_id` | reject シーケンスNo. | `BIGSERIAL` |
| `source_system` | 入力元種別 | `VARCHAR(50)` |
| `source_file_name` | ファイル名 | `VARCHAR(255)` |
| `source_row_no` | 行番号 | `INTEGER` |
| `reject_reason_cd` | reject 理由コード | `VARCHAR(50)` |
| `reject_reason_detail` | reject 理由詳細 | `TEXT` |
| `raw_payload_json` | 元行データ（JSON） | `TEXT` |
| `ingest_batch_id` | 取込実行ID | `VARCHAR(30)` |
| `created_at` | reject 記録時間 | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

#### `raw_payload_json` に含める内容

`raw_payload_json` には、**元ファイルの対象行を key-value 形式で JSON 化した内容をそのまま保持**する。

- 元行に存在した列は、採用列・捨て列を問わずすべて含める
- 正規化後の中間データではなく、元入力行そのものを保持する
- JSON 内のキー順は問わない
- reject 調査時に元データを追跡できることを優先する

#### reject 対象となる条件（入力不正）

以下は **入力不正** として reject する（業務異常とは区別する）。

| reject 理由コード例 | 内容 |
|---|---|
| `MISSING_REQUIRED` | 必須列欠損 |
| `DATE_PARSE_ERROR` | 日付変換失敗 |
| `END_BEFORE_START` | `end_ts < start_ts` |
| `NEGATIVE_ELAPSED` | `elapsed_sec < 0` |
| `NEGATIVE_WORK_SEC` | `work_sec < 0` |
| `WORK_EXCEEDS_ELAPSED` | `work_sec > elapsed_sec` |
| `INVALID_PROCESS_NAME` | `process_name` が未定義値 |
| `INVALID_RESULT_CD` | `result_cd` が未定義値 |
| `INVALID_SOURCE_SYSTEM` | `source_system` が未定義値 |
| `DUPLICATE_KEY` | `UNIQUE (order_no, process_name)` 違反 |

#### 業務異常（reject しない）

以下は形式上は正しく `work_log` に登録するが、KPI や個別分析で扱う。

- 作業時間が極端に長い / 短い
- 特定工程だけ NG が多い
- 同一作業者に負荷が偏っている
- 工程間滞留が偏在している

---

### 4.3 制約・インデックス

#### 主キー・一意制約

```sql
PRIMARY KEY (work_log_id)
UNIQUE (order_no, process_name)
```

1製番1工程1回という業務前提を DB 制約で保証する。

#### CHECK 制約

```sql
CHECK (process_name IN ('内装組立', '外装組立', '出荷検査'))
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

#### インデックス

```sql
CREATE INDEX idx_work_log_process_end_ts ON work_log (process_name, end_ts);
CREATE INDEX idx_work_log_worker_end_ts  ON work_log (worker_name, end_ts);
CREATE INDEX idx_work_log_order_process  ON work_log (order_no, process_name);
```

| インデックス | 用途 |
|---|---|
| `process_name + end_ts` | 工程別時間別の作業台数実績 |
| `worker_name + end_ts` | 作業者ごとの日別作業台数 |
| `order_no + process_name` | 工程間滞留判定・工程別進捗確認 |

---

### 4.4 `ingest_batch_id` の生成ルール

`ingest_batch_id` は **1ファイルの取込ごとに 1 つ採番**する。  
1 回の CLI 実行で複数ファイルを処理する場合でも、ファイル単位で別 ID を付与する。

- `internal_assembly_log.csv` → 別 `ingest_batch_id`
- `external_assembly_log.csv` → 別 `ingest_batch_id`
- `shipping_inspection_log.csv` → 別 `ingest_batch_id`

ID 形式は以下を使用する。

```
ING_YYYYMMDD_HH24MISS_連番
```

例:

```
ING_20260105_081530_001
ING_20260105_081530_002
ING_20260105_081530_003
```

この形式により、同じファイルを再取込した場合でも別実行として識別でき、
主テーブルと reject テーブルを batch 単位で追跡できる。

> **補足**: 実務では取込実行単位を管理する `import_run` テーブルを設けると便利だが、
> 本テーマでは説明を簡潔にするため省略し、`ingest_batch_id` で代替する。
> 連番はアプリケーション実行時に採番し、DB の永続通し番号までは要求しない。

---

## 5. 元ログ詳細設計

工程ごとに性格の異なる3種類の元ログを想定する。

| # | 工程 | ログの性格 | 主な取込難点 |
|---|---|---|---|
| 1 | 内装組立 | 文脈補完が必要な設備生ログ | ファイル名から業務情報を補完する |
| 2 | 外装組立 | 業務列が多い実績ログ | 必要列の選別と列名マッピング |
| 3 | 出荷検査 | 判定を丸める検査ログ | 不良明細から `OK/NG` への丸め込み |

この順にすることで、取込難易度と業務意味付けの差を段階的に説明できる。

---

### 5.1 内装組立ログ（文脈補完が必要な設備生ログ）

#### 位置付け

設備から直接出力された生ログを想定する。
START / END の時刻情報が中心で、業務的な意味を十分に持たない。
ファイル名規則や補助情報を用いて、工程名・作業者名・入力元種別を補完して取り込む。

> **講師向けポイント**: 「設備データをそのまま入れる」のではなく、「業務データへ変換する」ことが必要という論点を示す。

#### 想定ファイル名

```
INTASM_YamadaTaro_202601.csv
```

ファイル名から `worker_name`（`YamadaTaro`）・`process_name`・`source_system` を補完する。

#### サンプル列名

| サンプル列名 | 型 | 必須 | 説明 |
|---|---|:---:|---|
| `start_date` | DATE相当文字列 | ○ | 作業開始日 |
| `start_time` | TIME相当文字列 | ○ | 作業開始時刻 |
| `start_marker` | 文字列 | ○ | `START` 固定 |
| `end_date` | DATE相当文字列 | ○ | 作業終了日 |
| `end_time` | TIME相当文字列 | ○ | 作業終了時刻 |
| `end_marker` | 文字列 | ○ | `END` 固定 |
| `order_no` | 文字列 | ○ | 受注No. |

#### 採用列 / 捨て列 / 変換ルール

| 区分 | 元ログ列 | 正規化先 | 変換ルール |
|---|---|---|---|
| 採用 | `order_no` | `order_no` | trim のみ |
| 採用 | `start_date` + `start_time` | `start_ts` | 連結して TIMESTAMP 化 |
| 採用 | `end_date` + `end_time` | `end_ts` | 連結して TIMESTAMP 化 |
| 補完 | ファイル名 | `worker_name` | ファイル名規則から抽出 |
| 補完 | ファイル名 | `process_name` | `内装組立` を固定付与 |
| 補完 | ファイル名 | `source_system` | `internal_assembly_tool` を固定付与 |
| 変換 | `start_ts`, `end_ts` | `elapsed_sec` | 単純差分秒を計算 |
| 変換 | `start_ts`, `end_ts` | `work_sec` | 稼働カレンダー控除後秒を計算 |
| 変換 | 固定値 | `result_cd` | `OK` を固定付与 |
| 捨て列 | `start_marker` | なし | `START` 確認後は保持しない |
| 捨て列 | `end_marker` | なし | `END` 確認後は保持しない |

> `product_name` は補助マスタ（`order_product_master.csv`）から `order_no` をキーに補完する。

#### reject 条件

- `order_no` が空
- `start_date` / `start_time` / `end_date` / `end_time` のいずれかが空
- `start_marker <> 'START'`
- `end_marker <> 'END'`
- 日時変換失敗
- `end_ts < start_ts`
- `UNIQUE (order_no, process_name)` 違反

---

### 5.2 外装組立ログ（業務列が多い実績ログ）

#### 位置付け

比較的整った実績ログを想定する。
受注No.・製品名・開始時刻・終了時刻・資材コードなど多くの業務列を持ち、
主テーブルへ比較的素直にマッピングできる。
ただし「全部使う」のではなく「必要な列だけを共通契約へ落とす」ことが重要。

> **講師向けポイント**: 業務列が多いログは整理されているように見えるが、KPI に必要な列と不要な列を切り分けるスキルが求められるという論点を示す。

#### 想定ファイル名

```
EXTASM_SatoKen_202601.csv
```

ファイル名から `worker_name`（`SatoKen`）を補完する。

#### サンプル列名

| サンプル列名 | 型 | 必須 | 説明 |
|---|---|:---:|---|
| `production_date_yymmdd` | 文字列 | ○ | 生産日（YYMMDD形式） |
| `check_no` | 文字列 | ○ | チェックNo. |
| `qr_read_ts` | DATETIME相当文字列 | ○ | 加工指示書QRコード読出時刻（→ `start_ts`） |
| `all_clear_ts` | DATETIME相当文字列 | ○ | 全消込終了時刻（→ `end_ts`） |
| `production_date` | DATE相当文字列 | △ | 生産日 |
| `packing_date` | DATE相当文字列 | △ | 梱包作業日 |
| `tehai_no` | 文字列 | △ | 生産手配No. |
| `order_no` | 文字列 | ○ | 受注No. |
| `product_name` | 文字列 | ○ | 製品名 |
| `width_mm` | 数値 | △ | 製品幅 |
| `height_mm` | 数値 | △ | 製品丈 |
| `material_code1` 〜 `material_code6` | 文字列 | × | 資材コード |
| `material_name1` 〜 `material_name6` | 文字列 | × | 資材名称 |
| `material_qty1` 〜 `material_qty6` | 数値 | × | 資材数量 |
| `process_count1` 〜 `process_count12` | 数値 | × | 処理数 |
| `qr_clear_count` | 数値 | × | QR読消込数 |
| `initial_clear_count` | 数値 | × | 初期消込数 |
| `forced_clear_count` | 数値 | × | 強制消込数 |
| `material_pick_count` | 数値 | × | 品揃資材数 |
| `error_code` | 文字列 | △ | エラーコード |

#### 採用列 / 捨て列 / 変換ルール

| 区分 | 元ログ列 | 正規化先 | 変換ルール |
|---|---|---|---|
| 採用 | `order_no` | `order_no` | trim のみ |
| 採用 | `product_name` | `product_name` | trim のみ |
| 採用 | `qr_read_ts` | `start_ts` | DATETIME 変換 |
| 採用 | `all_clear_ts` | `end_ts` | DATETIME 変換 |
| 補完 | ファイル名 | `worker_name` | ファイル名規則から抽出 |
| 補完 | 固定値 | `process_name` | `外装組立` を固定付与 |
| 補完 | 固定値 | `source_system` | `external_assembly_tool` を固定付与 |
| 変換 | `start_ts`, `end_ts` | `elapsed_sec` | 単純差分秒を計算 |
| 変換 | `start_ts`, `end_ts` | `work_sec` | 稼働カレンダー控除後秒を計算 |
| 変換 | `error_code` | `result_cd` | 空なら `OK`、空でなければ reject（本テーマでは簡略化のため中間値は設けない） |
| 捨て列 | `production_date_yymmdd` | なし | `start_ts` から代替可能 |
| 捨て列 | `production_date` | なし | `start_ts` から代替可能 |
| 捨て列 | `packing_date` | なし | 今回の KPI では未使用 |
| 捨て列 | `tehai_no` | なし | 今回の主表では保持しない |
| 捨て列 | `width_mm`, `height_mm` | なし | 今回の KPI では未使用 |
| 捨て列 | `material_code1` 〜 `material_code6` | なし | KPI に未使用 |
| 捨て列 | `material_name1` 〜 `material_name6` | なし | KPI に未使用 |
| 捨て列 | `material_qty1` 〜 `material_qty6` | なし | KPI に未使用 |
| 捨て列 | `process_count1` 〜 `process_count12` | なし | KPI に未使用 |
| 捨て列 | `qr_clear_count` / `initial_clear_count` / `forced_clear_count` / `material_pick_count` | なし | KPI に未使用 |

#### reject 条件

- `order_no` が空
- `product_name` が空
- `qr_read_ts` または `all_clear_ts` が空
- 日時変換失敗
- `end_ts < start_ts`
- `error_code` が空でない（値の種別によらず一律 reject）
- `UNIQUE (order_no, process_name)` 違反

---

### 5.3 出荷検査ログ（判定を丸める検査ログ）

#### 位置付け

検査工程の帳票・検査システム出力を想定する。
作業時刻・受注No.に加えて、不良明細や不適合内訳を多く持つ。
そのまま主テーブルへ入れるのではなく、判定結果を `OK / NG` へ丸めて取り込む。

> **講師向けポイント**: 検査ログは `OK / NG` を直接持たない場合がある。明細値から共通結果コードへ丸めることが KPI 化の前提であるという論点を示す。

#### 想定ファイル名

```
SHIPCHK_202601.csv
```

`worker_name` は列 `inspector_name` から取得する（ファイル名補完不要）。

#### サンプル列名

| サンプル列名 | 型 | 必須 | 説明 |
|---|---|:---:|---|
| `inspector_name` | 文字列 | ○ | 担当者名（→ `worker_name`） |
| `inspection_date` | DATE相当文字列 | ○ | 検査日 |
| `slip_no` | 文字列 | △ | 伝票No. |
| `product_name` | 文字列 | ○ | 製品名 |
| `start_time` | TIME相当文字列 | ○ | 開始時間 |
| `end_time` | TIME相当文字列 | ○ | 終了時間 |
| `work_minutes` | 数値 | △ | 作業時間（分）※参考値 |
| `tehai_no` | 文字列 | △ | 生産手配No. |
| `order_no` | 文字列 | ○ | 受注No. |
| `bottom_ng_count` | 数値 | △ | ボトム不適合数 |
| `slat_ng_count` | 数値 | △ | スラット不適合数 |
| `balance_ng_count` | 数値 | △ | バランス不適合数 |
| `ng_total` | 数値 | ○ | 不良合計（→ `result_cd` 判定に使用） |

#### 採用列 / 捨て列 / 変換ルール

| 区分 | 元ログ列 | 正規化先 | 変換ルール |
|---|---|---|---|
| 採用 | `order_no` | `order_no` | trim のみ |
| 採用 | `product_name` | `product_name` | trim のみ |
| 採用 | `inspector_name` | `worker_name` | trim のみ |
| 採用 | `inspection_date` + `start_time` | `start_ts` | 連結して TIMESTAMP 化 |
| 採用 | `inspection_date` + `end_time` | `end_ts` | 連結して TIMESTAMP 化 |
| 補完 | 固定値 | `process_name` | `出荷検査` を固定付与 |
| 補完 | 固定値 | `source_system` | `shipping_inspection_tool` を固定付与 |
| 変換 | `start_ts`, `end_ts` | `elapsed_sec` | 単純差分秒を計算 |
| 変換 | `start_ts`, `end_ts` | `work_sec` | 稼働カレンダー控除後秒を計算 |
| 変換 | `ng_total` | `result_cd` | `0` → `OK` / `1以上` → `NG` |
| 捨て列 | `slip_no` | なし | 今回の KPI では未使用 |
| 捨て列 | `tehai_no` | なし | 今回の主表では保持しない |
| 捨て列 | `work_minutes` | なし | `start_ts` / `end_ts` から再計算可能 |
| 捨て列 | `bottom_ng_count` / `slat_ng_count` / `balance_ng_count` | なし | `result_cd` 丸め後は未使用 |

#### reject 条件

- `order_no` が空
- `product_name` が空
- `inspector_name` が空
- `inspection_date` / `start_time` / `end_time` のいずれかが空
- 日時変換失敗
- `ng_total` が数値変換できない
- `end_ts < start_ts`
- `UNIQUE (order_no, process_name)` 違反

---

### 5.4 3ログ共通の正規化先

| 物理名 | 内装組立 | 外装組立 | 出荷検査 |
|---|---|---|---|
| `order_no` | `order_no` | `order_no` | `order_no` |
| `product_name` | マスタ補完 | `product_name` | `product_name` |
| `process_name` | `内装組立`（固定） | `外装組立`（固定） | `出荷検査`（固定） |
| `worker_name` | ファイル名から補完 | ファイル名から補完 | `inspector_name` |
| `start_ts` | `start_date` + `start_time` | `qr_read_ts` | `inspection_date` + `start_time` |
| `end_ts` | `end_date` + `end_time` | `all_clear_ts` | `inspection_date` + `end_time` |
| `elapsed_sec` | 差分計算 | 差分計算 | 差分計算 |
| `work_sec` | カレンダー控除 | カレンダー控除 | カレンダー控除 |
| `result_cd` | `OK`（固定） | `error_code` から判定 | `ng_total` から判定 |
| `source_system` | `internal_assembly_tool` | `external_assembly_tool` | `shipping_inspection_tool` |

---

## 6. 取込処理の設計方針

### 入口と中核の分離

| 区分 | 用途 |
|---|---|
| CLI（入口） | 定時バッチ・大量処理 |
| Streamlit（入口） | 手動アップロード・エラー確認・例外対応 |
| `ingest_core`（中核） | 変換・検証・登録ロジックを集約 |

入口が違っても同じ判定基準で取り込めるよう、ロジックを中核に集約する。

### 取込フロー

```
1. ファイル受領
2. source_system 判定
3. 元フォーマットごとの列名マッピング
4. 型変換
5. 必須チェック
6. 値域チェック
7. elapsed_sec / work_sec 計算
8. 正常データと reject データへ振り分け
9. ingest_batch_id を付与
10. work_log へ登録
11. work_log_reject へ登録
12. 取込サマリを記録・表示
```

### 二重取込の保証

同じファイルを2回取り込んでも、`UNIQUE (order_no, process_name)` 制約により
`work_log` の件数は増加しない。
2回目以降の重複行は `work_log_reject` に `DUPLICATE_KEY` として記録される。

---

## 7. サンプルデータ設計

### 7.1 サンプル CSV イメージ

#### 内装組立ログ（`INTASM_YamadaTaro_202601.csv`）

```csv
start_date,start_time,start_marker,end_date,end_time,end_marker,order_no
2026-01-05,08:12:10,START,2026-01-05,08:24:40,END,ORD-260105-001
2026-01-05,08:28:05,START,2026-01-05,08:43:15,END,ORD-260105-002
2026-01-05,08:47:20,START,2026-01-05,09:05:00,END,ORD-260105-003
2026-01-06,08:05:45,START,2026-01-06,08:21:30,END,ORD-260106-001
2026-01-06,08:26:10,START,2026-01-06,08:44:55,END,ORD-260106-002
```

#### 外装組立ログ（`EXTASM_SatoKen_202601.csv`）

```csv
production_date_yymmdd,check_no,qr_read_ts,all_clear_ts,production_date,packing_date,tehai_no,order_no,product_name,width_mm,height_mm,material_code1,material_name1,material_qty1,material_code2,material_name2,material_qty2,qr_clear_count,initial_clear_count,forced_clear_count,material_pick_count,error_code
260105,CHK0001,2026-01-05 09:18:10,2026-01-05 09:33:20,2026-01-05,2026-01-05,TH-260105-001,ORD-260105-001,RS-90X180-WH,900,1800,MAT-A01,HeadRail-WH,1,MAT-B11,Fabric-WH,1,1,1,0,2,
260105,CHK0002,2026-01-05 09:37:40,2026-01-05 09:54:10,2026-01-05,2026-01-05,TH-260105-002,ORD-260105-002,RS-120X200-GY,1200,2000,MAT-A01,HeadRail-WH,1,MAT-B12,Fabric-GY,1,1,1,0,2,
260105,CHK0003,2026-01-05 10:02:05,2026-01-05 10:20:25,2026-01-05,2026-01-05,TH-260105-003,ORD-260105-003,VB-50-80X150-IV,800,1500,MAT-C21,Slat-IV,24,MAT-C31,LadderTape-IV,2,1,1,0,2,
260106,CHK0004,2026-01-06 09:11:30,2026-01-06 09:28:00,2026-01-06,2026-01-06,TH-260106-001,ORD-260106-001,RS-90X180-BE,900,1800,MAT-A01,HeadRail-WH,1,MAT-B13,Fabric-BE,1,1,1,0,2,
260106,CHK0005,2026-01-06 09:36:50,2026-01-06 09:55:40,2026-01-06,2026-01-06,TH-260106-002,ORD-260106-002,VT-80X200-LG,800,2000,MAT-D11,CarrierSet,1,MAT-D21,Louver-LG,8,1,1,0,2,
```

#### 出荷検査ログ（`SHIPCHK_202601.csv`）

```csv
inspector_name,inspection_date,slip_no,product_name,start_time,end_time,work_minutes,tehai_no,order_no,bottom_ng_count,slat_ng_count,balance_ng_count,ng_total
SuzukiMika,2026-01-05,SLP-260105-001,RS-90X180-WH,10:05:00,10:14:00,9,TH-260105-001,ORD-260105-001,0,0,0,0
SuzukiMika,2026-01-05,SLP-260105-002,RS-120X200-GY,10:18:00,10:28:00,10,TH-260105-002,ORD-260105-002,0,0,0,0
SuzukiMika,2026-01-05,SLP-260105-003,VB-50-80X150-IV,10:34:00,10:46:00,12,TH-260105-003,ORD-260105-003,0,0,0,0
SuzukiMika,2026-01-06,SLP-260106-001,RS-90X180-BE,10:02:00,10:11:00,9,TH-260106-001,ORD-260106-001,0,0,0,0
SuzukiMika,2026-01-06,SLP-260106-002,VT-80X200-LG,10:18:00,10:30:00,12,TH-260106-002,ORD-260106-002,0,0,0,0
```

#### 補助マスタ（`order_product_master.csv`）

内装組立ログの `product_name` 補完用。

```csv
order_no,product_name
ORD-260105-001,RS-90X180-WH
ORD-260105-002,RS-120X200-GY
ORD-260105-003,VB-50-80X150-IV
ORD-260106-001,RS-90X180-BE
ORD-260106-002,VT-80X200-LG
```

---

### 7.2 意図的に含める不正データ

不正データは **元ログ固有の誤り** に寄せて設計する。
`process_name` や `result_cd` は取込時に固定付与・丸め込みで決まるため、
元ファイル上での誤記という形では現れない点に注意。

#### 内装組立ログに混ぜる不正パターン

| 元ログ上の誤り | 期待する reject 理由コード |
|---|---|
| `order_no` が空白 | `MISSING_REQUIRED` |
| `start_date` に不正値（例: `2026-13-05`） | `DATE_PARSE_ERROR` |
| `start_marker` が `BEGIN` など `START` 以外 | `INVALID_MARKER` |
| `end_marker` が `STOP` など `END` 以外 | `INVALID_MARKER` |
| `end_time` が `start_time` より前（時刻逆転） | `END_BEFORE_START` |
| 同一 `order_no` の行を2行記録（重複） | `DUPLICATE_KEY` |

#### 外装組立ログに混ぜる不正パターン

| 元ログ上の誤り | 期待する reject 理由コード |
|---|---|
| `order_no` が空白 | `MISSING_REQUIRED` |
| `product_name` が空白 | `MISSING_REQUIRED` |
| `qr_read_ts` に不正値（例: `2026/99/05 09:00:00`） | `DATE_PARSE_ERROR` |
| `all_clear_ts` が `qr_read_ts` より前（時刻逆転） | `END_BEFORE_START` |
| `error_code` に値あり（例: `E001`） | `ERROR_CODE_PRESENT` |
| 列ズレにより `order_no` 列に製品名が入っている | `DATE_PARSE_ERROR` 等 |

#### 出荷検査ログに混ぜる不正パターン

| 元ログ上の誤り | 期待する reject 理由コード |
|---|---|
| `order_no` が空白 | `MISSING_REQUIRED` |
| `inspector_name` が空白 | `MISSING_REQUIRED` |
| `ng_total` が数値以外（例: `－`、`未記入`） | `NUM_PARSE_ERROR` |
| `inspection_date` に不正値（例: `20260105` 形式ズレ） | `DATE_PARSE_ERROR` |
| `end_time` が `start_time` より前（時刻逆転） | `END_BEFORE_START` |

#### 全工程共通

| パターン | 期待する reject 理由コード |
|---|---|
| 同じファイルを2回取り込む（全行が重複） | `DUPLICATE_KEY` |

#### 二重取込の確認ポイント

同じファイルを2回取り込んだ後、以下を確認する。

- `work_log` のレコード件数が増加していないこと
- `work_log_reject` に `DUPLICATE_KEY` が記録されていること
- 2回目の `ingest_batch_id` が別IDになっていること

---

### 7.3 作成ステップ

| Step | 内容 |
|---|---|
| 1 | サンプル列名を固定し、3フォーマットの雛形 CSV を作る |
| 2 | 採用列と捨て列を確定する |
| 3 | 変換ルールを確定する（日時結合・補完方法・丸め方・時間計算） |
| 4 | reject 条件とサンプル不正データの対応を定義する |
| 5 | 正常データを先に作る（2026-01-05 〜 2026-01-30 の営業日19日分） |
| 6 | 異常データを後から差し込む |
| 7 | 正規化結果を確認し、KPI の3指標が問題なく算出できることを確認する |

---

## 8. 今後の作業

以下は本ドキュメントの次段階として設計・実装する。

- [x] 期待正規化結果サンプル（`sample_expected_work_log.csv`）← 2026-01-05 分 9件作成済み
- [ ] サンプル CSV 全件作成（営業日19日分 × 3工程）
- [ ] 不正データ差し込み済みサンプル CSV の作成
- [ ] PostgreSQL DDL（CREATE TABLE 文）
- [ ] 取込スクリプト `ingest_core` の実装
- [ ] CLI 取込エントリーポイントの実装
- [ ] Streamlit 画面の要件定義と実装
  - 工程別時間別の作業台数実績グラフ
  - 工程間滞留の可視化（15分粒度）
  - 作業者別日次実績グラフ

---

## 9. 実装前提と補足仕様

本 README は設計ガイドとして十分な情報を持つが、AI によるコード生成では、**実装前提・境界条件・受入期待値** を追加で固定したほうがブレが少ない。  
本節は、そのための補足仕様である。

### 9.1 実装前提

本テーマでは、CLI 入力と Web 入力（Streamlit）を両方扱う。  
ただし、入口が違っても、判定・変換・reject 判定・DB 登録のロジックは共通化する。  

今回の規模では、過度な分割は行わず、**責務が明確になる最小構成**を採用する。  

#### ファイル構成

```text
results_record_db/
├─ README.md
├─ results_record_db_LOCAL_POSTGRESQL_SETUP.md
├─ ddl/
│  └─ ddl_results_record_db.sql
├─ sample_data/
│  ├─ internal_assembly/
│  ├─ external_assembly/
│  └─ shipping_inspection/
├─ src/
│  ├─ ingest.py
│  ├─ db.py
│  ├─ ingest_cli.py
│  └─ streamlit_app.py
└─ tests/
   ├─ test_ingest.py
   ├─ test_duplicate.py
   └─ test_kpi.py
```

#### 各ファイルの責務

| ファイル | 役割 |
|---|---|
| `ingest.py` | 共通取込ロジック。列マッピング、型変換、必須チェック、値域チェック、reject 判定、DB 登録を行う。 |
| `db.py` | SQLAlchemy を利用した DB 接続、モデル定義、セッション管理を行う。 |
| `ingest_cli.py` | CLI 入口。ファイルパスや入力元を受け取り、`ingest.py` を呼び出す。 |
| `streamlit_app.py` | Web 入口と KPI 表示。アップロードファイルを受け取り `ingest.py` を呼び出し、表示時は `db.py` を利用する。 |
| `tests/` | 主に `ingest.py` と KPI 集計処理を検証する。 |

#### DB 接続情報の扱い

本テーマのコードは **セミナー用のローカル検証コード** として作成するため、  
DB 接続情報は `db.py` にハードコードする。

想定接続先:

- PostgreSQL 18.3
- ローカルホスト
- DB 名: `results_record_db`
- ロール名: `results_user`
- パスワード: `results_pass`

本実装は恒久運用を前提としない。セミナー終了後に DB リソースを削除する前提で扱う。
Quick Start および Prompt Examples を作成する場合も、接続設定は環境変数ではなく `db.py` のハードコード前提で記載する。

#### 実装上の原則

- CLI と Web に業務ロジックを書かない。
- 共通ロジックは `ingest.py` に集約する。
- DB アクセスは `db.py` に集約する。
- Streamlit も `db.py` を通じて PostgreSQL を利用する。
- 入口は分けるが、判定基準は統一する。

### 9.2 `work_sec` 算出の境界条件

`work_sec` は、`start_ts` から `end_ts` の間に含まれる **稼働時間帯のみ** を積算した秒数とする。  
以下のルールを固定する。

| 条件 | 扱い |
|---|---|
| 稼働時間前（08:00 より前） | 08:00 に切り上げる |
| 稼働時間後（17:00 より後） | 17:00 に切り下げる |
| 昼休み（12:00〜13:00） | 全量控除する |
| 稼働時間外のみの記録 | `work_sec = 0` とする |
| `end_ts < start_ts` | reject |
| `work_sec > elapsed_sec` | reject |
| `work_sec < 0` | reject |

#### `work_sec` の跨日ルール

`start_ts` と `end_ts` が日付をまたぐ場合でも、形式上は正常データとして扱う。  
`work_sec` は期間全体を一括評価せず、**各日ごとに稼働時間帯（08:00〜12:00, 13:00〜17:00）のみを積算**して算出する。

例:

- `start_ts = 2026-01-05 16:50`
- `end_ts   = 2026-01-06 08:10`

この場合、

- 2026-01-05 の `16:50〜17:00` = 600 秒
- 2026-01-06 の `08:00〜08:10` = 600 秒

合計 `work_sec = 1200` とする。

ただし、`end_ts < start_ts` は reject とする。

#### 具体例

| start_ts | end_ts | elapsed_sec | work_sec | 理由 |
|---|---|---:|---:|---|
| 2026-01-05 11:50 | 2026-01-05 12:10 | 1200 | 600 | 12:00〜12:10 は昼休みとして控除 |
| 2026-01-05 07:50 | 2026-01-05 08:10 | 1200 | 600 | 08:00 前は非稼働時間として控除 |
| 2026-01-05 16:50 | 2026-01-05 17:10 | 1200 | 600 | 17:00 後は非稼働時間として控除 |
| 2026-01-05 12:10 | 2026-01-05 12:40 | 1800 | 0 | 全時間帯が昼休み |

補足: 土日・祝日データは、本テーマでは原則サンプルに含めない。含まれた場合は reject ではなく `work_sec = 0` として扱ってもよいが、今回のサンプルでは非対象とする。

### 9.3 ファイル名からの `worker_name` 抽出規則

内装組立・外装組立ログでは、`worker_name` はファイル名から抽出する。

対象パターン:

- `INTASM_YamadaTaro_202601.csv`
- `EXTASM_SatoKen_202601.csv`

正規表現:

`^(INTASM|EXTASM)_([A-Za-z]+)_\\d{6}\\.csv$`

抽出規則:

- グループ 2 を `worker_name` とする

例:

- `INTASM_YamadaTaro_202601.csv` → `worker_name = YamadaTaro`
- `EXTASM_SatoKen_202601.csv` → `worker_name = SatoKen`

なお、出荷検査ログ（`SHIPCHK_202601.csv`）ではファイル名からは抽出せず、列 `inspector_name` を `worker_name` として使用する。

### 9.4 `worker_name` 正規化ルール

`worker_name` は題材上そのまま保持するが、表記ゆれは取込時に吸収する。  
最低限、以下を実施する。

| 正規化項目 | 方針 |
|---|---|
| 前後空白 | 除去する |
| 全角 / 半角スペース | 除去する |
| 連続空白 | 1つに圧縮せず、題材上は除去で統一する |
| 大文字 / 小文字 | 英字はタイトルケースではなく、そのまま保持してもよい |
| 漢字 / ローマ字変換 | 本テーマでは自動変換しない |
| 別名統合 | 必要なものだけ辞書で統合する |

#### 最低限の辞書例

| 入力値 | 正規化後 |
|---|---|
| 山田太郎 | 山田太郎 |
| 山田　太郎 | 山田太郎 |
| 山田 太郎 | 山田太郎 |
| YamadaTaro | YamadaTaro |

補足: 漢字名とローマ字名の完全統合までは本テーマでは扱わない。  
ここを過度に広げると、題材の焦点が「名前マスタ整備」へ逸れるため。

### 9.5 `source_row_no` の基点

`source_row_no` は、**CSV / Excel ともに、ヘッダ行を除いたデータ行を 1 始まりで記録する**。  
Excel 取込時も、先頭行をヘッダとして解釈した場合のデータ行番号を記録する。

例:

- ヘッダ直下の最初のデータ行 → `source_row_no = 1`
- 2 行目のデータ行 → `source_row_no = 2`

Python 実装上の 0 始まり index をそのまま記録せず、表示・保存時は 1 始まりへ変換する。

### 9.6 duplicate の扱い

本テーマでは、重複判定の業務キーは `UNIQUE (order_no, process_name)` とする。

#### 実装方針

- 主テーブル登録時に UNIQUE 制約違反が発生した場合、その行は reject テーブルへ `DUPLICATE_KEY` として記録する。
- そのうえで、主テーブル側の件数は増えないことを保証する。
- つまり、「重複は黙って捨てる」のではなく、理由付きで監査可能にする。

#### 受入観点

- 同一ファイルを 2 回取り込んでも `work_log` の件数は増えない。
- 2 回目以降の重複行は `work_log_reject` に記録される。
- `ingest_batch_id` により、どの取込実行で発生した reject か追跡できる。

### 9.7 テストの期待値

サンプルデータを用いた最低限のテスト観点を以下に固定する。

| テスト観点 | 期待値 |
|---|---|
| 正常データ取込 | `work_log` に登録される |
| 必須欠損 | `work_log_reject` に記録される |
| 日時変換失敗 | `work_log_reject` に記録される |
| `end_ts < start_ts` | `work_log_reject` に記録される |
| duplicate | `work_log` 件数は増えず、`work_log_reject` に記録される |
| KPI 1 | 工程別時間別の作業台数を集計できる |
| KPI 2 | 工程間滞留を算出できる |
| KPI 3 | 作業者ごとの日別作業台数を集計できる |

#### セミナー用の最低受入条件

- reject が理由付きで分かれること。
- 二重取込で件数が増えないこと。
- KPI 3種が Streamlit 上で描画できること。

補足: 厳密な件数期待値は、サンプル CSV 作成後に別ファイルへ固定してもよい。  
本 README では、まず「何を確認すべきか」を固定する。

### 9.8 Streamlit 画面の最小要件

本テーマの Streamlit 画面は、見栄えよりも **KPI が確認でき、説明できること** を優先する。
BOP は Streamlit 内で  
`["内装組立", "外装組立", "出荷検査"]`  
の固定配列として扱う。
作業者マスターはサンプルデータから事前生成した CSV を利用してよい

#### 画面構成

| 項目 | 方針 |
|---|---|
| 画面数 | 1画面でも可 |
| 表示方式 | タブ分割またはセクション分割でも可 |
| 必須フィルタ | 期間、工程、作業者 |
| 出力 | CSV 出力を持つ |
| グラフ | 棒グラフまたは折れ線グラフで可 |
| 詳細表 | 元集計表を併記する |

#### KPI ごとの最低表示要件

| KPI | 最低要件 |
|---|---|
| 工程別時間別の作業台数 | `process_name × 時間帯` の集計が見える |
| 工程間滞留 | `order_no` ごとの工程間差分を元に、15分粒度で分布が見える |
| 作業者ごとの日別作業台数 | `worker_name × 日付` の集計が見える |

工程間滞留を評価する際には、工程の流れを示すBOP情報が必要であるが、今回のセミナーでは専用テーブルを作成せず、
**内装組立 → 外装組立 → 出荷検査**という規定の流れを元に、**内装組立 → 外装組立**と**外装組立 → 出荷検査**の2点の仕掛り量の推移を扱う。
このBOP情報はStreamlit内にハードコーディングで実装する。また、工程別時間別の作業台数も、工程の流れ順に表示をおこなうように実装する。

作業者ごとの日別作業台数における作業者は、あらかじめサンプルで用意したデータから作業者名称を抽出し、マスター化したものを利用する。

補足: Streamlit の部品や装飾は自由だが、**フィルタ → 集計 → 表示 → CSV 出力** の流れが確認できることを優先する。

### 9.9 実装時の基本姿勢

本テーマでは、AI にコードを起こさせるが、以下を原則とする。

- 先に README の文書を固める。
- 生成されたコードはそのまま採用せず、必ずレビューする。
- 論点は「1発で生成できるか」ではなく「仕様どおりか」。
- 実行デモは事前検証済み版で行う。

このため、AI に渡すプロンプトでは「コードを書け」ではなく、  
**この README に従って DDL / 取込処理 / Streamlit UI を作成せよ** という形で、文書を一次情報として扱う。


---

## 10. アーキテクチャ図

本テーマの全体像は、以下の構成で捉える。

```text
3種類の元ログ
  ├─ 内装組立ログ
  ├─ 外装組立ログ
  └─ 出荷検査ログ
          ↓
共通取込処理（Python / SQLAlchemy）
  ├─ 列マッピング
  ├─ 型変換
  ├─ 必須チェック
  ├─ 値域チェック
  ├─ reject 判定
  └─ DB 登録
          ↓
PostgreSQL
  ├─ work_log
  └─ work_log_reject
          ↓
KPI 集計
  ├─ 工程別時間別の作業台数
  ├─ 工程間滞留
  └─ 作業者ごとの日別作業台数
          ↓
Streamlit
  ├─ フィルタ
  ├─ グラフ表示
  ├─ 詳細表
  └─ CSV 出力
```

### 10.1 入口と共通ロジックの分離

本テーマでは、取込の入口は複数あってよいが、判定・変換・登録のロジックは共通化する。

```text
CLI 入力  ─┐
           ├─→ 共通取込処理（ingest.py） ─→ PostgreSQL
Web 入力  ─┘
```

- CLI は自動連携・一括処理向け
- Web は手動アップロード・例外確認向け
- ただし、どちらも同じ基準で `work_log` / `work_log_reject` へ反映する

### 10.2 本テーマでの実装ファイルとの対応

| 層 | 主な役割 | 想定ファイル |
|---|---|---|
| 入口（CLI） | ファイルパスや入力元を受け取り、共通取込処理を呼ぶ | `src/ingest_cli.py` |
| 入口（Web） | アップロードファイルを受け取り、共通取込処理を呼ぶ | `src/streamlit_app.py` |
| 共通取込処理 | 列マッピング、型変換、必須チェック、値域チェック、reject 判定、DB 登録 | `src/ingest.py` |
| DB 層 | SQLAlchemy による接続、モデル定義、セッション管理 | `src/db.py` |
| 表示層 | KPI 集計、グラフ表示、CSV 出力 | `src/streamlit_app.py` |

補足: 本テーマはセミナー題材のため、責務を明確にしつつ、過度なファイル分割は行わない。

## 11. 用語集

本テーマで使う用語を以下に整理する。

| 用語 | 意味 |
|---|---|
| 業務モデル | 何を単位に記録し、工程がどう流れるか、何を 1 レコードとみなすかを定義したもの |
| KPI | 最終的に見たい評価指標。本テーマでは「工程別時間別の作業台数」「工程間滞留」「作業者ごとの日別作業台数」の 3 種 |
| 正規化 | 異なる元ログを、共通の意味を持つカラムへ揃えて取り込める形にすること |
| `work_log` | 正常に取り込まれた作業実績を保持する主テーブル |
| `work_log_reject` | 取り込めなかった行を、理由付きで保持する reject テーブル |
| reject | 入力不正や制約違反などにより、主テーブルへ登録せず別管理すること |
| データ契約 | 何を正しいデータとみなすかを定義した合意。列、型、同一判定、例外条件などを含む |
| 受入条件 | どこまでできたら完成とみなすかを定義した合意。YES / NO で確認できる形にする |
| 運用ガードレール | 誰がいつ実行し、失敗時にどう対応するかを定義した合意 |
| `elapsed_sec` | `end_ts - start_ts` の単純差分秒 |
| `work_sec` | 昼休みや非稼働時間帯を除外した正味作業時間秒 |
| `ingest_batch_id` | 1 回の取込実行を識別する ID。主テーブルと reject テーブルを batch 単位で追跡するために使う |
| duplicate | 同じ業務キーのデータが重複して投入されること。本テーマでは `UNIQUE (order_no, process_name)` で防止する |
| `source_system` | どの元ログから取り込んだかを表す入力元種別 |
| BOP | 工程の流れ順を表す情報。本テーマでは専用テーブルを作らず、内装組立 → 外装組立 → 出荷検査を固定で扱う |
| Streamlit | Python で Web 画面を素早く作るためのフレームワーク。本テーマでは KPI 表示と手動取込 UI に利用する |
| SQLAlchemy | Python から DB を扱うためのライブラリ。本テーマでは PostgreSQL 接続とモデル定義に利用する |
| 共通取込処理 | CLI / Web のどちらから呼んでも同じ判定・変換・登録を行う中核ロジック。本テーマでは `ingest.py` が担当する |
| Quick Start | 題材の全体像を短時間で掴み、最短で動かすための導入手順 |
| Prompt Examples | AI に実装を依頼する際の指示例。DocDD では文書を一次情報として渡すことが重要になる |

### 11.1 本テーマで特に重要な用語

#### データ契約

「何を正とみなすか」を固定するための定義。  
本テーマでは、列・型・UNIQUE・CHECK・reject 条件・正規化ルールがここに含まれる。

#### 受入条件

「何をもって完成とするか」を固定するための定義。  
本テーマでは、reject が正しく記録されること、重複で件数が増えないこと、KPI 3 種が描画できることが最低条件となる。

#### 運用ガードレール

「誰がどう回すか」を固定するための定義。  
本テーマでは、CLI / Web の入口を分けつつロジックは共通化すること、ローカル PostgreSQL で検証できること、デモは事前検証済み版で行うことが相当する。
