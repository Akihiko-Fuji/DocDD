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
   - 9.8 [Streamlit 画面仕様（開発初期指示と最終仕様）](#98-streamlit-画面仕様開発初期指示と最終仕様)
   - 9.9 [実装時の基本姿勢](#99-実装時の基本姿勢)
10. [アーキテクチャ図](#10-アーキテクチャ図)
   - 10.1 [入口と共通ロジックの分離](#101-入口と共通ロジックの分離)
   - 10.2 [本テーマでの実装ファイルとの対応](#102-本テーマでの実装ファイルとの対応)
   - 10.3 [業務工程の流れ](#103-業務工程の流れ)
   - 10.4 [CLI/WebUI から見える状態までの流れ](#104-cliwebui-から見える状態までの流れ)
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

今回のセミナーに合わせて、実際にありそうな**工程の流れを簡略化する形**でデザインしたものです。

作業実績ログは、[`make_sample_data.md`](./make_sample_data.md)というログデータの設計ドキュメントを制作し、
ドキュメントを元にAIに製作させたものであり、実際の生産工程データではありません。

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

データベースの設計はデータ運用のノウハウが必要な領域ですので不慣れな場合、
インプット情報(今回は生産実績ログ)とアウトプット情報(今回はKPI)を元に、
AIと共に実装仕様の検討を進めていくのが良いです。

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

| reject 理由コード | 内容 |
|---|---|
| `MISSING_REQUIRED` | 必須列欠損 |
| `DATE_PARSE_ERROR` | 日付変換失敗 |
| `END_BEFORE_START` | `end_ts < start_ts` |
| `WORK_EXCEEDS_ELAPSED` | `work_sec > elapsed_sec` |
| `INVALID_RESULT_CD` | `result_cd` が未定義値 |
| `ERROR_CODE_PRESENT` | 外装組立ログの `error_code` が空でない |
| `INVALID_WORKER_NAME` | `worker_name` をファイル名/行データから解決できない |
| `DUPLICATE_KEY` | `UNIQUE (order_no, process_name)` 違反 |
| `MASTER_NOT_FOUND` | `order_no` に対応する `product_name` が補助マスタに存在しない |
| `DB_CONSTRAINT_ERROR` | DB 制約違反など `DUPLICATE_KEY` 以外の登録エラー |

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


> 前提メモ: 本テーマは **1製番 × 1工程 = 1レコード** を前提とする（`UNIQUE (order_no, process_name)` で担保）。
> 将来この制約を緩める場合は、KPI2 の「次工程の最初の完了」の定義（同一製番・同一工程の複数行選択ルール）を別途仕様化すること。

### 4.4 `ingest_batch_id` の生成ルール

`ingest_batch_id` は **1ファイルの取込ごとに 1 つ採番**する。  
1 回の CLI 実行で複数ファイルを処理する場合でも、ファイル単位で別 ID を付与する。

- `INTASM_YamadaTaro_202601.csv` → 別 `ingest_batch_id`
- `EXTASM_SatoKen_202601.csv` → 別 `ingest_batch_id`
- `SHIPCHK_202601.csv` → 別 `ingest_batch_id`

ID 形式は以下を使用する。

```text
ING_YYYYMMDD_HH24MISS_連番
```

例:

```text
ING_20260105_081530_001
ING_20260105_081530_002
ING_20260105_081530_003
```

この形式により、同じファイルを再取込した場合でも別実行として識別でき、
主テーブルと reject テーブルを batch 単位で追跡できる。

> 本テーマでは `ingest_batch_id` に **マイクロ秒は採用しない**。  
> 形式は `ING_YYYYMMDD_HH24MISS_連番` に統一する。
> **補足**: 実務では取込実行単位を管理する `import_run` テーブルを設けると便利だが、
> 本テーマでは説明を簡潔にするため省略し、`ingest_batch_id` で代替する。
>
> 本テーマの ingest_batch_id はセミナー用の追跡ラベルであり、DB上の厳密な一意性までは保証しない。  
> 同一秒に複数プロセスから取込を実行するような本番運用では、import_run テーブル、DBシーケンス、UUID等による実行ID管理を検討する。
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

```text
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

```text
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

```text
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

```text
1. ファイル受領
2. ファイル名プレフィックスで取込種別を判定（`INTASM_...` / `EXTASM_...` / `SHIPCHK_...`）
3. 判定結果に応じて `source_system` を付与（`internal_assembly_tool` / `external_assembly_tool` / `shipping_inspection_tool`）
4. 元フォーマットごとの列名マッピング
5. 型変換
6. 必須チェック
7. 値域チェック
8. elapsed_sec / work_sec 計算
9. 正常データと reject データへ振り分け
10. ingest_batch_id を付与
11. work_log へ登録
12. work_log_reject へ登録
13. 取込サマリを記録・表示
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
| `start_marker` が `BEGIN` など `START` 以外 | `MISSING_REQUIRED` |
| `end_marker` が `STOP` など `END` 以外 | `MISSING_REQUIRED` |
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
| `ng_total` が数値以外（例: `－`、`未記入`） | `INVALID_RESULT_CD` |
| `inspection_date` に不正値（例: `20260105` 形式ズレ） | `DATE_PARSE_ERROR` |
| `end_time` が `start_time` より前（時刻逆転） | 出荷検査のみ翌営業日へ補正して取り込む（reject しない） |

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

以下は初版README作成時のTODOだったが、**2026年5月時点では実装済み**。

- [x] 期待正規化結果サンプル（`sample_expected_work_log.csv`）← 2026-01-05 分 9件作成済み
- [x] サンプル CSV 全件作成（営業日19日分 × 3工程）
- [x] 不正データ差し込み済みサンプル CSV の作成
- [x] PostgreSQL DDL（CREATE TABLE 文）
- [x] 取込スクリプト `ingest_core` の実装
- [x] CLI 取込エントリーポイントの実装
- [x] Streamlit 画面の要件定義と実装
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
│  ├─ INTASM_HanaYamada_202601.csv
│  ├─ EXTASM_MunekiYoshimura_202601.csv
│  ├─ SHIPCHK_202601.csv
│  ├─ INTASM_HanaYamada_202601_invalid.csv
│  ├─ EXTASM_MunekiYoshimura_202601_invalid.csv
│  ├─ SHIPCHK_202601_invalid.csv
│  └─ order_product_master.csv
├─ sample_expected_work_log.csv
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
| `work_sec < 0` | 本実装の算出手順では発生しない（`calc_work_sec` は非負のみ返す） |

#### `work_sec` の跨日ルール

`start_ts` と `end_ts` が日付をまたぐ場合でも、形式上は正常データとして扱う。  
`work_sec` は期間全体を一括評価せず、**各日ごとに稼働時間帯（08:00〜12:00, 13:00〜17:00）のみを積算**して算出する。
このとき、ループ対象日が非稼働日（土日・`2026-01-12`）の場合は、その日の `work_sec` は `0` 秒として扱う。

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

補足: 本テーマはセミナー向け簡易実装のため、稼働カレンダーは「土日休み + 固定祝日 2026-01-12」のみを扱う。業務時間も `08:00-12:00` / `13:00-17:00` 固定とし、カレンダーマスタ連携は実装しない。


#### KPI1 の 17:00 枠に関する補足

KPI1 は `end_ts` の時間帯（`08:00`〜`17:00`）で件数を集計するため、**17:00 台の完了件数も表示対象**とする。
一方 `work_sec` は稼働時間帯のみを積算するため、`17:00` 以降の時間は算入しない。

- KPI1: 完了時刻ベースの件数
- `work_sec`: 勤務時間内の正味作業時間

このため、17:00 完了枠が表示されても、17:00 以降の作業秒数は `work_sec` へ含めない。

### 9.3 ファイル名からの `worker_name` 抽出規則

内装組立・外装組立ログでは、`worker_name` はファイル名から抽出する。

加えて、行データ側に `worker_name` 列が存在する場合は、正規化後にファイル名由来の値と一致していることを必須とし、不一致は `INVALID_WORKER_NAME` で reject する。

対象パターン:

- `INTASM_YamadaTaro_202601.csv`
- `EXTASM_SatoKen_202601.csv`

正規表現（実装の `FILENAME_WORKER_RE` と同一）:

`^(INTASM|EXTASM)_([^_]+)_\\d{6}(?:\\d{2})?\\.(csv|xlsx|xlsm)$`

抽出規則:

- グループ 2 を `worker_name` とする（英字以外も許容、`_` は除外）

例:

- `INTASM_YamadaTaro_202601.csv` → `worker_name = YamadaTaro`
- `EXTASM_SatoKen_202601.csv` → `worker_name = SatoKen`

なお、出荷検査ログ（`SHIPCHK_202601.csv`）ではファイル名からは抽出せず、列 `inspector_name` を `worker_name` として使用する。

### 9.3.1 ファイル名プレフィックスによる取込種別判定

`ingest.py` の実装では、取込種別の判定は次のファイル名プレフィックスを正とする。

- `INTASM_...` → `process_name = 内装組立` / `source_system = internal_assembly_tool`
- `EXTASM_...` → `process_name = 外装組立` / `source_system = external_assembly_tool`
- `SHIPCHK_...` → `process_name = 出荷検査` / `source_system = shipping_inspection_tool`

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

> 注記（セミナー向け）: 同時実行時の厳密な排他制御（advisory lock や直列化制御）は今回の題材では実装しない。
> 競合時は DB 側 UNIQUE 制約で最終防衛し、`DUPLICATE_KEY` として reject 記録する方針とする。

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

AI にテスト実装を依頼するプロンプトでは、**テスト用 DB もローカルの `results_record_db` をそのまま使い、モックやフィクスチャは使わない**ことを明記する。

#### 目指すべきソフトウェア品質

ソフトウェアの品質の話単体で、セミナーが成り立つほどの領域ですので、今回のセミナーでは深追いはしません。

コード上のロジックが設計意図と乖離しないかはテストシナリオ及びテストコードを用いて、評価をおこなう前提となります。
テストシナリオは設計の中に組み込むのが望ましいのですが、不慣れな場合は、機能要件を元にAIと協議しながら明確にしていくのが適切です。

一方で、例外処理 Exception Handling に関しては、ソフトウェア的な知見や慎重さが要求される領域であり、機能要件を整理するだけでは明確になるものではありません。
私は利用用途別に下記のようなレベル分類をしています。

| レベル | グレード名 | 主な用途 | 品質の考え方 | 代表的な要求 |
|---:|---|---|---|---|
| 1 | 実験・ホビー品質 | 個人開発、学習、技術検証、使い捨てスクリプト | まず動くことを優先する | 最低限の動作確認、簡単なコメント、自分が読める程度の構成 |
| 2 | 便利ツール品質 | 社内ツール、小規模自動化、チーム内補助ツール | 少人数が安心して使えることを重視する | 基本的なエラー処理、README、設定値の外出し、簡単なログ、手動復旧可能な設計 |
| 3 | 業務・プロダクト品質 | SaaS、Webサービス、業務アプリ、顧客向けアプリ | 継続的に運用・保守・拡張できることを重視する | 自動テスト、CI/CD、コードレビュー、認証認可、監視、ログ、脆弱性対策、データ整合性 |
| 4 | ミッションクリティカル品質 | 24/365稼働システム、決済、物流、通信、大規模基盤、重要な組み込み | 障害が起きてもサービス全体が破綻しないことを重視する | 冗長化、フェイルオーバー、SLO/SLA、負荷試験、監視アラート、障害対応手順、バックアップ、監査ログ |
| 5 | セーフティ・社会インフラ品質 | 金融中枢、航空、鉄道、医療機器、プラント、電力、防衛、宇宙 | 失敗が人命・社会・巨大資産に影響する前提で、証明可能性と監査性を重視する | 規格準拠、形式的な検証、独立レビュー、要件トレーサビリティ、安全解析、厳格な変更管理、再現可能ビルド、長期保守 |

表を元に簡潔に整理すると、今回の用途を元に品質を検討する場合、今回のプログラムが目指す**レベルは3に相当**します。
ただし、今回のコードは実運用ではなくセミナー向けに構築するという前提であるため**レベル2の品質**を満たすことを要件として進めます。

AIコーディングを用いてソフトウェアの品質を高める場合、用途の明示化やテスト要件の明示化などをおこなったうえで、アウトプットされたコードに対して、品質の改善を目的としたアクションが別途必要です。
AIを用いた開発においても、品質要求はそのままコスト(=実装工数)となりますので、便利ツールにミッションクリティカル品質を要求するなどの要求は、適切ではありません。

また、ソフトウェア品質改善アプローチの手法としてCodexでコード生成する際に複数案を提示させて妥当な実装を選択する進め方もありますが、ソフトウェア開発の知見が十分にない中で比較できない場合、作成したコード差分を**ChatGPTや、Claude code、Code Rabbit**などの他のAIサービスにレビューを依頼し、**複数AIの視点からの指摘事項を元に実装品質を高めるアプローチ**も有効です。

いずれも、ソフトウェアを開発する段階で、どのような用途で利用するか**非機能要件として明示すること**が重要です。
例えば、業務・プロダクト品質であれば、エラーを詳細に分類し必要に応じてエラーでプログラムを終了させる選択が有効である一方で、ミッションクリティカル品質の場合、エラーログは残しつつも終了させないことを優先する場面もあります。その違いは、設計書にて明示しない限りAI側では判断が難しい要素となります。

### 9.8 Streamlit 画面仕様（開発初期指示と最終仕様）

この節は、**開発初期ドキュメント段階の指示**と、`src/streamlit_app.py` による**最終仕様**（実装を正とした仕様）を区別して記載する。  
レビュー時は両者の差分を確認し、プロトタイプからゴールに至る設計判断を追跡できるようにする。

#### 9.8.1 開発初期ドキュメント段階の指示（元の内容）

初期段階で固定していた指示は以下。

- 1画面でもよく、表示方式はタブ/セクションどちらでも可。
- 必須フィルタは「期間・工程・作業者」。
- KPI1/KPI2/KPI3 が確認できること。
- CSV 出力を持つこと。
- 工程順は BOP `内装組立 → 外装組立 → 出荷検査` を前提とすること。
- 作業者は事前抽出したサンプル由来マスターの利用を許容すること。

この段階は「最低要件の枠組み」を決めることが目的であり、実装の細部（再検証タイミング、バケット境界、異常系列の扱い等）は未確定だった。

#### 9.8.2 プロトタイプから最終仕様までの検討差分（抜け漏れ防止）

最終実装までの間に、以下の設計判断が追加・確定した。

- **Import の整合性設計**
  - 「検証・プレビュー」と「DB登録」を分離。
  - 登録直前に同一バイト列で `prepare_ingest_file` を再実行し、重複判定の一貫性を確保。
- **KPI2 の定義厳密化**
  - 工程ペアを2組固定（内装→外装、外装→出荷）。
  - 15分粒度の時点評価を 08:00〜16:45 で固定。
  - 同一製番で複数候補がある場合、`from_end` ごとに「`from_end` 以降最初の `to_end`」を採用。
  - `to_end < from_end` は監査情報として保持しつつ、推移カウントから除外。
- **UI の具体化**
  - 4タブ固定構成に統一。
  - KPIごとのCSVファイル名を固定。
  - データ欠損時/実行文脈外の挙動を明示。

#### 9.8.3 最終仕様（実装を正とした逆引き仕様）

ここでは `src/streamlit_app.py` の現行実装を正とし、画面仕様を逆引きで固定する。  
（README の記述と実装が矛盾した場合は、まず実装を確認してから README を更新する。）

#### 画面全体

- 1画面の Streamlit アプリで、タブは **4つ固定**。
  - `Import`
  - `KPI1 工程別時間別`
  - `KPI2 工程間滞留`
  - `KPI3 作業者別日別`
- BOP（工程順）は `['内装組立', '外装組立', '出荷検査']` を固定配列として扱う。
- 全体フィルタとして以下を持つ。
  - 期間（`date_input`。既定値はDB内の最小/最大日付）
  - 工程（複数選択、既定で全工程）
  - 作業者（複数選択、既定で全作業者）
- DBの `work_log` 読み込み時は、必要列を固定SQLで取得し、`end_ts` 基準で `work_date` と `hour_bucket` を算出する。

#### Import タブの仕様

- アップロード対応拡張子: `csv`, `xlsx`, `xlsm`。
- 操作は2段階。
  1. **検証・プレビュー**: `prepare_ingest_file` を実行し、候補/Reject候補を表示。
  2. **DBへ登録**: 同一アップロードバイト列を使って `prepare_ingest_file` を再実行後、`apply_ingest_plan` で登録。
- `DBへ登録` 前に prepare を再実行するのは、重複判定の整合性確保のため（同一トランザクション内で評価）。
- サンプルファイル互換のため、アップロードファイル名にはリネームマップを適用してから判定する。
- セッション状態で ingest 計画を保持し、別ファイルへの差し替え時は ingest 状態を破棄する。

#### KPI1（工程別時間帯別 作業件数）

- 集計条件は「期間・工程・作業者」で絞り込み。
- `end_ts` の時を `hour_order` とし、**08:00〜17:00 の10スロット固定**で表示。
- データがない時間帯・工程もゼロ件で補完し、工程順は BOP 順で表示。
- 表示は grouped bar（時間帯 × 工程）、CSV ダウンロード名は `kpi1_process_hourly.csv`。

#### KPI2（工程間滞留 15分足）

- 対象工程ペアは固定2組。
  - `内装組立 → 外装組立`
  - `外装組立 → 出荷検査`
- 時系列バケットは **08:00〜16:45 の15分刻み**。
- 滞留件数は「`from_end <= ts` かつ `to_end` が未完了または `to_end > ts`」でカウント。
- 同一 `order_no` に複数レコードがある場合は、`from_end` ごとに **`from_end` 以降で最初の `to_end`** を採用する。
  - `to_end < from_end` は `is_invalid_sequence=True` として明細に残す。
  - ただし滞留推移カウントには invalid sequence 行を使わない。
- 出力は推移（折れ線）と明細（表）を分け、CSV は以下の2種類。
  - `kpi2_stagnation_trend.csv`
  - `kpi2_stagnation_detail.csv`

#### KPI3（作業者別日別実績）

- 集計条件は「期間・工程・作業者」で絞り込み。
- 集計単位は `work_date × process_name × worker_name` の件数。
- 画面上はさらに工程を単一選択して、作業者別棒グラフ（日付色分け）を表示。
- CSV ダウンロード名は `kpi3_worker_daily.csv`。

#### エラー/空データ時の挙動

- DB読み込み失敗・必須列不足時はエラー表示し、空DataFrameとして継続。
- 表示対象データが空の場合は警告を表示し、フィルタ・タブUIは維持する。
- Streamlit 実行コンテキスト外（`python streamlit_app.py` 直実行など）では、ガイダンス文を標準出力して終了する。

#### 画面表示例
上記の設計にてStreamlitで画面表示をおこなった際の実装例は下記となる。

<img width="2980" height="600" alt="output" src="https://github.com/user-attachments/assets/aae3932e-c32a-4a7c-93fa-0cd7e1345c17" />

グラフなどに使用する色にルールを持たせる場合は、その旨をドキュメントに明示しておくなどでUI/UXの改善を進めるのが望ましい。

#### 9.8.4 KPI定義と評価ロジックの妥当性

KPI画面では、グラフが表示されること自体よりも、  
**そのKPIが業務上の意味と一致しているか** が重要である。

特に KPI2「工程間滞留」は、単にSQLやPythonで件数を数えればよいものではない。  
まず、業務上の「仕掛り」または「工程間滞留」をどう定義するかを固定する必要がある。

本テーマでは、工程間滞留を以下のように定義する。

| 区間 | 滞留として数える状態 |
|---|---|
| 内装組立 → 外装組立 | 内装組立が完了済みで、外装組立が未完了 |
| 外装組立 → 出荷検査 | 外装組立が完了済みで、出荷検査が未完了 |

時点 `ts` における滞留判定は、以下の条件で行う。

```text
from_end <= ts
かつ
to_end が存在しない、または to_end > ts
```

つまり、前工程が終わっていて、後工程がまだ終わっていない状態を、  
その時点の工程間滞留として扱う。

この定義は、今回のセミナー用モデルに合わせた簡略化である。  
実務で利用する場合は、以下のような論点を別途確認する必要がある。

| 論点 | 確認内容 |
|---|---|
| 工程順 | 実際の工程順が固定か、分岐や戻りがあるか |
| 記録単位 | 1製番=1台でよいか、ロット・束・明細単位が必要か |
| 完了時刻 | どの時刻を工程完了とみなすか |
| 対象時間 | 稼働時間外・休日・休憩時間をどう扱うか |
| 異常データ | 後工程完了が前工程完了より前の場合をどう扱うか |
| 除外条件 | reject済みデータ、重複、工程欠落をどう扱うか |
| 集計粒度 | 日別、時間別、15分足など、どの粒度で見るか |

したがって、KPIの妥当性はコードだけでは担保できない。  
以下の順で担保する。

1. 業務上のKPI定義を文書化する
2. 計算ロジックを仕様として明記する
3. 代表的な製番・工程データを使って期待値を作る
4. 手計算または既存管理表と突合する
5. 必要に応じて、現場実測データと並行評価する
6. 期待値をテストケース化する

##### 現場実測による妥当性確認

仕掛りや工程間滞留のようなKPIは、システム上のログだけで妥当性を判断しづらい場合がある。  
そのため実務では、システム計算値とは別に、現場で観測できる実測情報を取得し、並行して突合する方法が有効である。

例えば、仕掛りであれば以下のような確認が考えられる。

| 確認方法 | 内容 |
|---|---|
| 現場棚卸し | 指定時刻に、工程間に実際に残っている現品数を数える |
| 置き場・台車・棚番の確認 | 工程間置き場、仕掛り置き場、台車上の現品数を記録する |
| 代表製番の追跡 | 特定の製番を選び、前工程完了から後工程完了までの動きを追う |
| 既存管理表との突合 | 現場で既に使っているExcelやホワイトボードの仕掛り数と比較する |
| 時刻別サンプリング | 10:00、13:00、15:00 など、決めた時刻で実測値とシステム計算値を比較する |
| 写真・現場記録との照合 | 必要に応じて、置き場写真や現場記録と照合する |

このとき重要なのは、システム計算値と現場実測値が完全一致することだけを目的にしないことである。  
差異が出た場合は、以下のどれに該当するかを確認する。

| 差異の原因 | 例 |
|---|---|
| KPI定義の違い | 現場は「置き場にある数」を数えているが、システムは「後工程未完了数」を数えている |
| 記録タイミングの違い | 実際の作業完了と、ログ記録時刻にズレがある |
| 工程外の滞留 | 検査待ち、手直し待ち、搬送待ちなどが工程定義に含まれていない |
| データ欠落 | 一部工程の完了ログが記録されていない |
| 例外処理 | reject済みデータや異常順序データの扱いが実測と異なる |

この突合により、KPIロジックそのものの誤りだけでなく、  
業務上の定義不足、記録タイミングのズレ、現場実態との乖離を発見できる。

つまり、仕掛り推移の妥当性は、以下の2つを合わせて確認する。

```text
システム上のイベントログから計算した値
+
現場で実際に観測した値
```

この両者を突合し、差異の理由を説明できる状態にすることで、  
KPIを「きれいなグラフ」ではなく、業務判断に使える指標に近づけることができる。

本テーマでは、説明を分かりやすくするため、KPI2は固定工程順・固定工程ペア・15分粒度の時点評価として実装している。  
実案件では、KPI定義そのものを業務側と合意し、その定義に基づいて受入条件、テスト観点、現場実測による突合方法を作成する必要がある。

DocDDの観点では、KPI定義も仕様の一部である。  
グラフの見た目だけでなく、**その数値が何を意味し、どの条件で算出され、現場実態とどう照合するか** を文書として残すことが重要である。

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


### 10.3 業務工程の流れ

本テーマで扱う業務上の工程は、BOP として **内装組立 → 外装組立 → 出荷検査** の固定順とする。  
各工程は別々のツール・帳票からログを出力するが、`order_no` をキーに同一製番の工程進捗として結び付ける。

```mermaid
flowchart LR
    order["受注 / 製番発行<br/>order_no"] --> internal["内装組立<br/>設備生ログ<br/>INTASM_*.csv"]
    internal --> external["外装組立<br/>実績ログ<br/>EXTASM_*.csv"]
    external --> inspection["出荷検査<br/>検査ログ<br/>SHIPCHK_*.csv"]
    inspection --> shipped["出荷可能状態"]

    internal -. 完了時刻 end_ts .-> kpi2a["工程間滞留<br/>内装 → 外装"]
    external -. 完了時刻 end_ts .-> kpi2a
    external -. 完了時刻 end_ts .-> kpi2b["工程間滞留<br/>外装 → 出荷"]
    inspection -. 完了時刻 end_ts .-> kpi2b
```

この図で重要なのは、ログの入力順ではなく、**業務上の工程順**と**工程完了時刻 `end_ts`** を基準に KPI を評価する点である。  
特に KPI2 は、前工程が完了し、次工程が未完了の時間帯を工程間滞留として数える。

### 10.4 CLI/WebUI から見える状態までの流れ

CLI と WebUI は入口が異なるだけで、どちらも共通取込処理を経由して `work_log` / `work_log_reject` に反映する。  
その後、Streamlit が DB を読み込み、フィルタ・グラフ・詳細表・CSV 出力としてユーザーに見える状態にする。

```mermaid
flowchart TD
    subgraph Input["入力入口"]
        cli["CLI<br/>src/ingest_cli.py<br/>定時バッチ・一括取込"]
        web_import["WebUI: Import タブ<br/>src/streamlit_app.py<br/>手動アップロード"]
    end

    cli --> core["共通取込処理<br/>src/ingest.py"]
    web_import --> preview["検証・プレビュー<br/>prepare_ingest_file"]
    preview --> register["DBへ登録<br/>登録直前に再検証"]
    register --> core

    subgraph Core["共通取込処理の主な責務"]
        core --> detect["ファイル種別判定<br/>INTASM / EXTASM / SHIPCHK"]
        detect --> map["列マッピング・補完<br/>product_name / worker_name 等"]
        map --> validate["型変換・必須チェック・値域チェック"]
        validate --> calc["elapsed_sec / work_sec 計算"]
        calc --> split{"正常行か?"}
    end

    split -- "正常" --> work_log[("PostgreSQL<br/>work_log")]
    split -- "不正・重複" --> reject[("PostgreSQL<br/>work_log_reject")]

    work_log --> load["Streamlit DB読込<br/>期間・工程・作業者フィルタ"]
    reject --> import_result["Import タブ<br/>Reject候補・登録結果・理由確認"]
    load --> kpi1["KPI1<br/>工程別時間別 作業件数"]
    load --> kpi2["KPI2<br/>工程間滞留 15分足"]
    load --> kpi3["KPI3<br/>作業者別日別実績"]
    kpi1 --> visible["ユーザーから見える状態<br/>グラフ / 詳細表 / CSV出力"]
    kpi2 --> visible
    kpi3 --> visible
    import_result --> visible
```

WebUI では、登録前に「検証・プレビュー」を表示し、登録直前にも同一アップロード内容で再検証する。  
これにより、画面で見た取込候補・Reject候補と、DB 登録時の判定がずれないようにする。


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
| データコントラクト | 何を正しいデータとみなすかを定義した合意。列、型、同一判定、例外条件などを含む |
| 受入条件 | どこまでできたら完成とみなすかを定義した合意。YES / NO で確認できる形にする |
| 運用ガードレール | 誰がいつ実行し、失敗時にどう対応するかを定義した合意 |
| `elapsed_sec` | `end_ts - start_ts` の単純差分秒 |
| `work_sec` | 昼休みや非稼働時間帯を除外した正味作業時間秒 |
| `ingest_batch_id` | 1 ファイルの取込単位を識別する ID。主テーブルと reject テーブルを file-batch 単位で追跡するために使う |
| duplicate | 同じ業務キーのデータが重複して投入されること。本テーマでは `UNIQUE (order_no, process_name)` で防止する |
| `source_system` | どの元ログから取り込んだかを表す入力元種別 |
| BOP | 工程の流れ順を表す情報。本テーマでは専用テーブルを作らず、内装組立 → 外装組立 → 出荷検査を固定で扱う |
| Streamlit | Python で Web 画面を素早く作るためのフレームワーク。本テーマでは KPI 表示と手動取込 UI に利用する |
| SQLAlchemy | Python から DB を扱うためのライブラリ。本テーマでは PostgreSQL 接続とモデル定義に利用する |
| 共通取込処理 | CLI / Web のどちらから呼んでも同じ判定・変換・登録を行う中核ロジック。本テーマでは `ingest.py` が担当する |
| Quick Start | 題材の全体像を短時間で掴み、最短で動かすための導入手順 |
| Prompt Examples | AI に実装を依頼する際の指示例。DocDD では文書を一次情報として渡すことが重要になる |

### 11.1 本テーマで特に重要な用語

#### データコントラクト

「何を正とみなすか」を固定するための定義。  
本テーマでは、列・型・UNIQUE・CHECK・reject 条件・正規化ルールがここに含まれる。

#### 受入条件

「何をもって完成とするか」を固定するための定義。  
本テーマでは、reject が正しく記録されること、重複で件数が増えないこと、KPI 3 種が描画できることが最低条件となる。

#### 運用ガードレール

「誰がどう回すか」を固定するための定義。  
本テーマでは、CLI / Web の入口を分けつつロジックは共通化すること、ローカル PostgreSQL で検証できること、デモは事前検証済み版で行うことが相当する。
出荷検査ログでは、inspection_date + end_time が inspection_date + start_time より前になる場合、  
翌営業日の終了時刻として扱う。土日および 2026-01-12 は営業日から除外する。  
これは検査記録の運用上、日付欄が開始日基準で記録されるケースを想定した補正であり、  
内装組立・外装組立には適用しない。
