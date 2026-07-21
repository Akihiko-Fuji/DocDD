# results_record_db 設計ガイド

## 概要

本ドキュメントは、**複数の設備機器から異なるフォームで出力される実績データ**を、
共通ルールで正規化して PostgreSQL に取り込み、
最終的に Streamlit で KPI を可視化するシステムの **設計・開発ガイド**である。

セミナー題材として、現場でよくある以下の状況を模している。

- 工程ごとに利用ツールが異なる → ログのフォーマットが異なる
- ログの列名・時刻表現・粒度が揃っていない
- そのままでは KPI 評価に使えない

> `sample_data/` と `sample_expected_work_log.csv` は、教材用に生成した架空データである。氏名、受注番号、製品、作業実績は実在する人物・企業・業務データを表さない。

| 区分 | 本文での意味 | 規範性 |
|---|---|---|
| 仕様 | 実装・テストが必ず満たす断定事項（must / shall） | 規範 |
| 解説 | その仕様を採用する理由・設計意図 | 非規範 |
| 教材コメント | 初心者が理解するための具体例・補足・学習上のポイント | 非規範 |

> **規範性:** 実装・テストの判断は「仕様」のみを正とする。「解説」と「教材コメント」は非規範であり、仕様と矛盾する場合は仕様を優先する。
>
> **仕様の記述規則:** 仕様欄では「できるだけ」「原則として」「必要に応じて」「なるべく」「適切に」「など」「基本的に」を単独で使用しない。これらの語を使用する場合は、適用条件・対象・例外・判定基準を列挙し、実装・テストで YES / NO を判定できる文にする。
>
> 悪い例: `必要に応じて reject する。`  
> 良い例: `以下のいずれかに該当する行は reject する。`

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

**仕様**

- 1製番を1台の個体識別単位とし、`order_no` で3工程を接続する。
- 1製番・1工程につき1レコードとし、工程順は内装組立 → 外装組立 → 出荷検査に固定する。
- `order_no` は前後空白だけを除去し、ハイフン、記号、英字の大文字・小文字を保持する。
- サンプルでは `ORD-YYMMDD-NNN` 形式を使用する。

**解説**

最初に記録単位と工程順を固定することで、DBの一意制約、重複判定、工程間滞留の意味を同じ基準で設計できる。
`order_no` の記号を削除すると異なる番号を同一視する可能性があるため、見た目を揃える目的の過度な正規化は行わない。

**仕様**

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

**教材コメント**

今回のセミナーに合わせて、実際にありそうな**工程の流れを簡略化する形**でデザインしたものです。

作業実績ログは、[`make_sample_data.md`](./make_sample_data.md)というログデータの設計ドキュメントを制作し、
ドキュメントを元にAIに製作させたものであり、実際の生産工程データではありません。

---

## 2. 最終的な評価 KPI

**仕様**

- KPI1は `end_ts` を基準に工程別・時間別の完了台数を集計する。
- KPI2は前工程の `end_ts` から次工程の `start_ts` まで、次工程未着手の製番数を15分粒度で集計する。
- KPI3は `end_ts` の日付を基準に、作業者・工程・日別の完了台数を集計する。

**解説**

KPIを先に定義すると、取込時に残す列と捨てる列を判断しやすい。
特にKPI2は、次工程で作業中の製品を工程間滞留へ含めないため、次工程の完了時刻ではなく開始時刻を使用する。

**仕様**

| # | KPI | 集計軸 |
|---|---|---|
| 1 | 工程別時間別の作業台数実績 | `process_name` × `end_ts`（時間帯） |
| 2 | 工程間の滞留状態 | `order_no` × 工程間の時間差（15分粒度） |
| 3 | 作業者ごとの日別作業台数 | `worker_name` × `end_ts`（日付） |

---

## 3. ゴール

**仕様**

- 異なる3種類のログを共通形式へ変換し、正常行とreject行を追跡可能な状態で保存する。
- 正規化後のデータからKPI 3種をStreamlitで表示し、表とCSVでも確認できるようにする。
- 仕様、実装、テストの対応関係を説明できる成果物とする。

**解説**

この題材のゴールは画面を表示することだけではない。
入力データの意味を揃え、異常行を説明でき、KPIの計算結果をテストできるところまでを一つの流れとして扱う。

**仕様**

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

**仕様**

- 正常実績用の `work_log` と、取込不可行用の `work_log_reject` を作成する。
- 業務上の一意性と値域をDB制約でも保証し、KPIの検索軸に合わせてインデックスを作成する。

**解説**

アプリケーション側の検証だけでは、別経路からの登録や同時実行時の不整合を完全には防げない。
DB制約を最終防衛として併用し、rejectテーブルによって失敗理由を追跡可能にする。

**教材コメント**

データベースの設計はデータ運用のノウハウが必要な領域ですので不慣れな場合、
インプット情報(今回は生産実績ログ)とアウトプット情報(今回はKPI)を元に、
AIと共に実装仕様の検討を進めていくのが良いです。

### 4.1 主テーブル `work_log`

**仕様**

- 3種類の元ログを共通カラムへ正規化して保存する。
- `order_no`、工程、作業者、開始・終了時刻、作業時間、結果、入力元、取込追跡情報を保持する。
- `order_no` は入力値の前後空白だけを除去して保存する。

**解説**

元ログ固有の列をすべて持ち込むのではなく、3工程で同じ意味を持つ情報へ揃える。
共通形に変換しておくことで、画面側が入力元ごとの違いを意識せずに集計できる。

**仕様**

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

**仕様**

- 主テーブルへ登録できなかった行を、理由コード、詳細、元行JSON、取込IDとともに保存する。
- `raw_payload_json` には採用列・未使用列を問わず、元行の全列を保持する。

**解説**

異常行を黙って捨てると、入力件数と登録件数の差を説明できない。
元行と理由を残すことで、データ修正、再取込、原因分析に利用できる。

**仕様**

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
| `MISSING_REQUIRED` | 必須列欠損、必須値空、または内装組立ログの `START` / `END` マーカー不一致 |
| `DATE_PARSE_ERROR` | 日付変換失敗 |
| `END_BEFORE_START` | `end_ts < start_ts` |
| `WORK_EXCEEDS_ELAPSED` | `work_sec > elapsed_sec` |
| `INVALID_RESULT_CD` | `result_cd` が未定義値 |
| `ERROR_CODE_PRESENT` | 外装組立ログの `error_code` が空でない |
| `INVALID_WORKER_NAME` | 内装・外装ログの任意列 `worker_name` が、ファイル名から抽出した作業者名と正規化後に一致しない |
| `DUPLICATE_KEY` | `UNIQUE (order_no, process_name)` 違反 |
| `MASTER_NOT_FOUND` | `order_no` に対応する `product_name` が補助マスタに存在しない |
| `DB_CONSTRAINT_ERROR` | `DUPLICATE_KEY` 以外のDB登録エラー（CHECK、NOT NULL、型、長さの制約違反を含む） |

**解説**

従来の簡潔な説明も、用語の導入として次のとおり残す。詳細な判定条件は上表および後続の優先順位を正とする。

> | `MISSING_REQUIRED` | 必須列欠損 |
> | `INVALID_WORKER_NAME` | `worker_name` をファイル名/行データから解決できない |

#### reject理由の判定優先順位

1入力行が複数の異常条件に該当した場合は、最初に成立した1件だけを `reject_reason_cd` として記録する。同じ行に複数のrejectレコードは作成しない。

| 優先順位 | 判定 | 採用するreject理由 | 適用対象 |
|---:|---|---|---|
| 1 | 業務キー・必須値の欠損、内装組立のマーカー不一致 | `MISSING_REQUIRED` | 全ログ |
| 2 | 開始・終了日時のパース失敗 | `DATE_PARSE_ERROR` | 全ログ |
| 3 | 補助マスタ未登録 | `MASTER_NOT_FOUND` | 内装組立 |
| 3 | `error_code` が空でない | `ERROR_CODE_PRESENT` | 外装組立 |
| 3 | `ng_total` を整数へ変換できない | `INVALID_RESULT_CD` | 出荷検査 |
| 4 | 任意列 `worker_name` とファイル名由来作業者の不一致 | `INVALID_WORKER_NAME` | 内装組立・外装組立 |
| 5 | 補正対象外の `end_ts < start_ts` | `END_BEFORE_START` | 内装組立・外装組立 |
| 6 | `work_sec > elapsed_sec` | `WORK_EXCEEDS_ELAPSED` | 全ログ |
| 7 | 事前重複判定で業務キーが一致 | `DUPLICATE_KEY` | 全ログ |
| 8 | DB登録時のUNIQUE制約違反 | `DUPLICATE_KEY` | 全ログ |
| 8 | DB登録時のUNIQUE制約以外のエラー | `DB_CONSTRAINT_ERROR` | 全ログ |

同じ優先順位3の条件はログ種別ごとに排他的であり、1行で相互に競合しない。出荷検査の `end_ts < start_ts` は翌営業日補正の対象であり、`END_BEFORE_START` を採用しない。

| 複合同時エラーの例 | 採用するreject理由 | 理由 |
|---|---|---|
| `order_no` が空、かつ日付形式が不正 | `MISSING_REQUIRED` | 必須値判定を日時パースより先に行う |
| 外装組立で `end_ts < start_ts`、かつ `error_code` が空でない | `ERROR_CODE_PRESENT` | 外装固有の `error_code` 判定を共通時刻整合性判定より先に行う |
| 事前重複判定に該当し、DB制約違反の可能性もある | `DUPLICATE_KEY` | 重複と判定した行はDB登録を実行しない |

#### 業務異常（reject しない）

以下は形式上は正しく `work_log` に登録するが、KPI や個別分析で扱う。

- 作業時間が極端に長い / 短い
- 特定工程だけ NG が多い
- 同一作業者に負荷が偏っている
- 工程間滞留が偏在している

---

### 4.3 制約・インデックス

**仕様**

- `UNIQUE (order_no, process_name)` で1製番・1工程・1レコードを保証する。
- 工程名、結果コード、入力元、時刻順、作業秒数をCHECK制約で検証する。
- KPIと重複判定で使用する検索軸にインデックスを設定する。

**解説**

一意制約は重複投入を防ぐだけでなく、KPI2で同一工程の複数候補を選ぶ必要がないことも明確にする。
将来、再加工を扱う場合は、試行番号や履歴テーブルを含めて別途設計する。

**仕様**

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
> 将来この制約を緩める場合は、KPI2 の「次工程の最初の開始」の定義（同一製番・同一工程に複数行がある場合の選択ルール）も合わせて仕様化すること。

### 4.4 `ingest_batch_id` の生成ルール

**仕様**

- 1ファイルの取込ごとに1つの `ingest_batch_id` を発行する。
- 形式は `ING_YYYYMMDD_HHMMSS_連番`、最大30文字とする。
- 同一ファイルの再取込でも別IDを発行する。

**解説**

正常行とreject行をファイル単位で追跡するためのラベルである。
本教材では説明を簡潔にするため取込実行テーブルを省略しており、本番のグローバル一意性までは保証しない。

**仕様**

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

**仕様**

- ファイル名またはプレフィックスからログ種別を判定する。
- 元ログごとに採用列、補完値、変換ルール、reject条件を固定する。
- 変換後は同じ `work_log` 契約へ揃える。

**解説**

3種類のログは、設備生ログ、業務列の多い実績ログ、検査ログという異なる難しさを持つ。
この違いを残すことで、単なるCSV読込ではなく、業務データへ意味付けする過程を説明できる。

**教材コメント**

工程ごとに性格の異なる3種類の元ログを想定する。

| # | 工程 | ログの性格 | 主な取込難点 |
|---|---|---|---|
| 1 | 内装組立 | 文脈補完が必要な設備生ログ | ファイル名から業務情報を補完する |
| 2 | 外装組立 | 業務列が多い実績ログ | 必要列の選別と列名マッピング |
| 3 | 出荷検査 | 判定を丸める検査ログ | 不良明細から `OK/NG` への丸め込み |

この順にすることで、取込難易度と業務意味付けの差を段階的に説明できる。

---

### 5.1 内装組立ログ（文脈補完が必要な設備生ログ）

**仕様**

- 日付・時刻・START/ENDマーカー・`order_no` を読み取る。
- 作業者、工程、入力元はファイル名と固定値から補完する。
- `product_name` は補助マスタから `order_no` 完全一致で取得する。

**解説**

設備ログだけでは製品名や作業者などの業務文脈が不足する。
ファイル名規則と補助マスタをデータ契約の一部として扱い、共通実績へ変換する例である。

**教材コメント**

#### 位置付け

設備から直接出力された生ログを想定する。
START / END の時刻情報が中心で、業務的な意味を十分に持たない。
ファイル名規則や補助情報を用いて、工程名・作業者名・入力元種別を補完して取り込む。

> **講師向けポイント**: 「設備データをそのまま入れる」のではなく、「業務データへ変換する」ことが必要という論点を示す。

**仕様**

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
| `worker_name` | 文字列 | × | 任意の互換列。値がある場合はファイル名由来の作業者名と照合する |

#### 採用列 / 捨て列 / 変換ルール

| 区分 | 元ログ列 | 正規化先 | 変換ルール |
|---|---|---|---|
| 採用 | `order_no` | `order_no` | trim のみ |
| 採用 | `start_date` + `start_time` | `start_ts` | 連結して TIMESTAMP 化 |
| 採用 | `end_date` + `end_time` | `end_ts` | 連結して TIMESTAMP 化 |
| 補完 | ファイル名 | `worker_name` | ファイル名規則から抽出 |
| 検証 | 任意列 `worker_name` | `worker_name` | 値がある場合は空白正規化後にファイル名由来値と比較し、不一致を `INVALID_WORKER_NAME` とする |
| 補完 | ファイル名 | `process_name` | `内装組立` を固定付与 |
| 補完 | ファイル名 | `source_system` | `internal_assembly_tool` を固定付与 |
| 変換 | `start_ts`, `end_ts` | `elapsed_sec` | 単純差分秒を計算 |
| 変換 | `start_ts`, `end_ts` | `work_sec` | 稼働カレンダー控除後秒を計算 |
| 変換 | 固定値 | `result_cd` | `OK` を固定付与 |
| 捨て列 | `start_marker` | なし | `START` 確認後は保持しない |
| 捨て列 | `end_marker` | なし | `END` 確認後は保持しない |

> `product_name` は補助マスタ（`order_product_master.csv`）から `order_no` をキーに補完する。

### データサンプル
[sample_data/INTASM_HanaYamada_202601.csv](https://github.com/Akihiko-Fuji/DocDD/blob/main/results_record_db/sample_data/INTASM_HanaYamada_202601.csv)


#### reject 条件

- `order_no` が空
- `start_date` / `start_time` / `end_date` / `end_time` のいずれかが空
- `start_marker <> 'START'`
- `end_marker <> 'END'`
- 日時変換失敗
- `end_ts < start_ts`
- 任意列 `worker_name` に値があり、空白正規化後の値がファイル名由来の作業者名と一致しない
- `UNIQUE (order_no, process_name)` 違反

---

### 5.2 外装組立ログ（業務列が多い実績ログ）

**仕様**

- `qr_read_ts` を開始、`all_clear_ts` を終了として使用する。
- `error_code` が空の行だけを正常登録し、値がある行はrejectする。
- 資材・寸法等の余剰列は主テーブルへ保存しないが、reject時の元行JSONには残す。

**解説**

列数が多いログでも、KPIに必要な情報が多いとは限らない。
目的から必要列を選ぶ一方、異常調査に必要な元データはreject側へ残す。
外装組立の `error_code` は製品品質の合否ではなく、設備・処理が正常完了しなかった状態を表す前提とする。出荷検査の `ng_total` のように `OK / NG` へ変換できる品質判定ではないため、`result_cd = NG` へ丸めず `ERROR_CODE_PRESENT` としてrejectする。

**教材コメント**

#### 位置付け

比較的整った実績ログを想定する。
受注No.・製品名・開始時刻・終了時刻・資材コードなど多くの業務列を持ち、
主テーブルへ比較的素直にマッピングできる。
ただし「全部使う」のではなく「必要な列だけを共通契約へ落とす」ことが重要。

> **講師向けポイント**: 業務列が多いログは整理されているように見えるが、KPI に必要な列と不要な列を切り分けるスキルが求められるという論点を示す。

**仕様**

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
| `worker_name` | 文字列 | × | 任意の互換列。値がある場合はファイル名由来の作業者名と照合する |
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
| 検証 | 任意列 `worker_name` | `worker_name` | 値がある場合は空白正規化後にファイル名由来値と比較し、不一致を `INVALID_WORKER_NAME` とする |
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

### データサンプル
[sample_data/EXTASM_MunekiYoshimura_202601.csv](https://github.com/Akihiko-Fuji/DocDD/blob/main/results_record_db/sample_data/EXTASM_MunekiYoshimura_202601.csv)


#### reject 条件

- `order_no` が空
- `product_name` が空
- `qr_read_ts` または `all_clear_ts` が空
- 日時変換失敗
- `end_ts < start_ts`
- `error_code` が空でない（値の種別によらず一律 reject）
- 任意列 `worker_name` に値があり、空白正規化後の値がファイル名由来の作業者名と一致しない
- `UNIQUE (order_no, process_name)` 違反

---

### 5.3 出荷検査ログ（判定を丸める検査ログ）

**仕様**

- `inspection_date` と開始・終了時刻からタイムスタンプを作成する。
- `inspector_name` を作業者として使用する。
- `ng_total = 0` を `OK`、1以上を `NG` へ変換する。
- 終了時刻が開始時刻より前の場合だけ、終了日を翌営業日に補正する。

**解説**

検査ログの不良明細を、共通の結果コードへ丸める例である。
翌営業日補正は出荷検査固有の運用を表現したもので、内装・外装ログへは適用しない。

**教材コメント**

#### 位置付け

検査工程の帳票・検査システム出力を想定する。
作業時刻・受注No.に加えて、不良明細や不適合内訳を多く持つ。
そのまま主テーブルへ入れるのではなく、判定結果を `OK / NG` へ丸めて取り込む。

> **講師向けポイント**: 検査ログは `OK / NG` を直接持たない場合がある。明細値から共通結果コードへ丸めることが KPI 化の前提であるという論点を示す。

**仕様**

#### 想定ファイル名

```text
SHIPCHK_202601.csv
```

`worker_name` は列 `inspector_name` から取得する（ファイル名補完不要）。

出荷検査ログでは、inspection_date + end_time が inspection_date + start_time より前になる場合、  
翌営業日の終了時刻として扱う。土日および 2026-01-12 は営業日から除外する。  
これは検査記録の運用上、日付欄が開始日基準で記録されるケースを想定した補正であり、  
内装組立・外装組立には適用しない。

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


### データサンプル
[sample_data/SHIPCHK_202601.csv](https://github.com/Akihiko-Fuji/DocDD/blob/main/results_record_db/sample_data/SHIPCHK_202601.csv)


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

**仕様**

- 3ログを同じカラム、型、許容値へ変換する。
- `order_no` は前後空白だけを除去し、ハイフン・記号・英字大小を保持する。
- `elapsed_sec` と `work_sec` はすべて同じ関数・稼働条件で算出する。

**解説**

共通化するのはファイルの見た目ではなく、データの意味である。
同じ製番、工程、時刻、結果を同じルールで扱えることが、後続KPIの前提になる。

**仕様**

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

#### 日時パース形式

日時パースで許容する形式を以下に限定する。対象値が必須値として空の場合は `MISSING_REQUIRED`、値が存在して形式に一致しない場合は `DATE_PARSE_ERROR` とする。

| ログ | 対象列 | 許容形式 |
|---|---|---|
| 内装組立 | `start_date` / `end_date` | `YYYY-MM-DD` または `YYYY/MM/DD` |
| 内装組立 | `start_time` / `end_time` | `HH:MM:SS` |
| 外装組立 | `qr_read_ts` / `all_clear_ts` | `YYYY-MM-DD HH:MM:SS` |
| 出荷検査 | `inspection_date` | `YYYY-MM-DD` |
| 出荷検査 | `start_time` / `end_time` | `HH:MM:SS` |

- 年は4桁とする。
- 月・日・時・分・秒は1桁または2桁を受理する。ゼロ埋めは推奨表記だが、パース条件にはしない。
- 秒は必須とし、`HH:MM` は受理しない。
- 小数秒、タイムゾーン、末尾の `Z`、ISO 8601の `T` 区切りは受理しない。
- 生成される `start_ts` / `end_ts` はタイムゾーン情報を持たないnaive datetimeとする。
- 外装組立の `production_date_yymmdd` は `YYMMDD` 形式だが、`start_ts` / `end_ts` の生成には使用しない。

---

## 6. 取込処理の設計方針

**仕様**

- CLIとWebは入口だけを分け、判定・変換・reject・DB登録を `src/ingest.py` に集約する。
- 登録前に検証計画を作り、正常候補とreject候補を分離する。
- 重複は事前判定とDBのUNIQUE制約で防止する。

**解説**

入口ごとに業務ロジックを持つと、同じファイルでも判定結果が変わる。
共通取込処理を一つにすることで、CLI・Web・テストが同じ仕様を使用できる。

### 入口と中核の分離

| 区分 | 用途 |
|---|---|
| CLI（入口） | 定時バッチ・大量処理 |
| Streamlit（入口） | 手動アップロード・エラー確認・例外対応 |
| `src/ingest.py`（中核） | 変換・検証・登録ロジックを集約 |

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

**仕様**

- `sample_data/generate_sample_data.py` を生成物の正本とし、固定乱数シードで再現可能にする。
- 19営業日、日別175〜275台の範囲で、3工程に同じ `order_no` を1回ずつ生成する。
- 上記の175〜275台を設計上の許容範囲とする。
- 正常3工程、補助マスタ、期待結果CSVの製番集合を一致させる。

**解説**

サンプルCSVと生成スクリプトの世代がずれると、教材の説明と実行結果が一致しない。
生成条件、配布CSV、期待値を一体として管理することで、デモを再現可能にする。

### 7.1 サンプル CSV イメージ

**仕様**

- 各ログの代表的な列構成と値の形式を、少数行のCSV例で示す。
- `order_no` は `ORD-YYMMDD-NNN` 形式で3工程を接続する。
- 実際に取り込むファイル名と全件データは `sample_data/` 配下を正とする。

**解説**

本文の少数行は列の意味を説明するためのイメージ例であり、ファイル名を含む実行用データは `sample_data/` 配下を使用する。
大量の実ファイルはKPIの傾向と性能差を確認するために使う。

**教材コメント**

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

**仕様**

- 必須欠損、日時不正、時刻逆転、エラーコード、結果不正、マスタ未登録、重複を含める。
- 各不正サンプル行には主な不正原因を1つだけ設定し、期待するreject理由を一意に特定できるようにする。

**解説**

正常データだけでは、仕様の境界や失敗時の説明可能性を確認できない。
意図した不正と理由コードを対応させることで、reject設計をデモできる。

**仕様**

不正データは **元ログ固有の誤り** に寄せて設計する。
`process_name` や `result_cd` は取込時に固定付与・丸め込みで決まるため、
元ファイル上での誤記という形では現れない点に注意。

#### 内装組立ログに混ぜる不正パターン

| 元ログ上の誤り | 期待する reject 理由コード |
|---|---|
| `order_no` が空白 | `MISSING_REQUIRED` |
| `start_date` に不正値（例: `2026-13-05`） | `DATE_PARSE_ERROR` |
| `start_marker` が `START` 以外（例: `BEGIN`） | `MISSING_REQUIRED` |
| `end_marker` が `END` 以外（例: `STOP`） | `MISSING_REQUIRED` |
| `end_time` が `start_time` より前（時刻逆転） | `END_BEFORE_START` |
| 同一 `order_no` の行を2行記録（重複） | `DUPLICATE_KEY` |

**解説**

`start_marker` / `end_marker` の不一致は値の欠損ではないが、本教材では理由コードを増やさず、必須マーカー条件を満たさない入力として `MISSING_REQUIRED` にまとめる。空値との違いは `reject_reason_detail` の `start_marker must be START` / `end_marker must be END` で識別する。

**仕様**

#### 外装組立ログに混ぜる不正パターン

| 元ログ上の誤り | 期待する reject 理由コード |
|---|---|
| `order_no` が空白 | `MISSING_REQUIRED` |
| `product_name` が空白 | `MISSING_REQUIRED` |
| `qr_read_ts` に不正値（例: `2026/99/05 09:00:00`） | `DATE_PARSE_ERROR` |
| `all_clear_ts` が `qr_read_ts` より前（時刻逆転） | `END_BEFORE_START` |
| `error_code` に値あり（例: `E001`） | `ERROR_CODE_PRESENT` |
| 列ズレにより `order_no` 列に製品名が入っている | `order_no` の値だけではrejectしない。列ズレで `qr_read_ts` / `all_clear_ts` が日時不正になった場合は `DATE_PARSE_ERROR`、必須値が空になった場合は `MISSING_REQUIRED` |

**解説**

従来の不正パターン表では、次のように簡略記載していた。

> | 列ズレにより `order_no` 列に製品名が入っている | `DATE_PARSE_ERROR` 等 |

上の「等」が表す分岐を、仕様表では日時不正、必須値空、`order_no` の値だけがずれた場合に分解して固定した。

**仕様**

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

**仕様**

- 生成スクリプトを実行して正常CSV、異常CSV、補助マスタ、期待結果CSVをまとめて生成する。
- 生成後に件数、製番集合、工程順、日別範囲、再現性を検証する。
- 現行生成値は19営業日、日別194〜244台、総4,321製番とする。
- この194〜244台は、設計上の許容範囲175〜275台に収まる固定生成結果である。

**解説**

CSVを個別に手修正すると整合性が崩れやすい。
修正は生成スクリプトへ反映し、すべての生成物を同時に更新する。

**教材コメント**

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

**仕様**

- 未完了作業と完了済み作業をチェックリストで明示する。
- 実装完了後も、仕様変更時はDDL、コード、テスト、サンプル、文書の同期を確認する。

**解説**

チェックリストは進捗表示だけでなく、成果物間の更新漏れを防ぐ役割を持つ。
セミナー前には実行環境と画面表示を含む最終確認を行う。

以下は初版README作成時のTODOだったが、**2026年5月時点では実装済み**。

- [x] 期待正規化結果サンプル（`sample_expected_work_log.csv`）← 2026-01-05 分 9件作成済み
- [x] サンプル CSV 全件作成（営業日19日分 × 3工程）
- [x] 不正データ差し込み済みサンプル CSV の作成
- [x] PostgreSQL DDL（CREATE TABLE 文）
- [x] 共通取込スクリプト `src/ingest.py` の実装
- [x] CLI 取込エントリーポイントの実装
- [x] Streamlit 画面の要件定義と実装
  - 工程別時間別の作業台数実績グラフ
  - 工程間滞留の可視化（15分粒度）
  - 作業者別日次実績グラフ

---

## 9. 実装前提と補足仕様

**仕様**

- 実装時に判断が分かれやすい境界条件、命名規則、重複、テスト、画面仕様を固定する。
- READMEを一次情報とし、実装・テストが本文の条件と一致することを確認する。

**解説**

概要だけではAIや実装者が一般論で仕様を補いやすい。
境界値と受入条件を明示することで、同じ文書から再実装しても判断がぶれにくくなる。

**仕様**

本 README は設計ガイドとして十分な情報を持つが、AI によるコード生成では、**実装前提・境界条件・受入期待値** を追加で固定したほうがブレが少ない。  
本節は、そのための補足仕様である。

### 9.1 実装前提

**仕様**

- `db.py`、`ingest.py`、`ingest_cli.py`、`streamlit_app.py` に責務を分ける。
- Python依存は `python -m pip install -r requirements.txt` で導入する。
- セミナー用のDB接続情報は `db.py` の固定値を使用する。

**解説**

過度な分割を避けつつ、DB、共通取込、CLI、Webの境界を明確にする。
依存を `requirements.txt` へ集約することで、`altair` 等の導入漏れと文書間の差を防ぐ。

**仕様**

本テーマでは、CLI 入力と Web 入力（Streamlit）を両方扱う。  
ただし、入口が違っても、判定・変換・reject 判定・DB 登録のロジックは共通化する。  

今回の規模では、過度な分割は行わず、**責務が明確になる最小構成**を採用する。  

#### ファイル構成

```text
results_record_db/
├─ README.md
├─ quickstart.md
├─ WINDOWS_SETUP.md
├─ results_record_db_LOCAL_POSTGRESQL_SETUP.md
├─ requirements.txt
├─ pytest.ini
├─ ddl/
│  └─ ddl_results_record_db.sql
├─ sample_data/
│  ├─ generate_sample_data.py
│  ├─ INTASM_HanaYamada_202601.csv
│  ├─ INTASM_KentoTakahashi_202601.csv
│  ├─ INTASM_HanaYamadaInvalid_202601.csv
│  ├─ EXTASM_MunekiYoshimura_202601.csv
│  ├─ EXTASM_ShuheiYamashita_202601.csv
│  ├─ EXTASM_ToshioAndo_202601.csv
│  ├─ EXTASM_MunekiYoshimuraInvalid_202601.csv
│  ├─ SHIPCHK_202601.csv
│  ├─ SHIPCHK_202601_invalid.csv
│  └─ order_product_master.csv
├─ sample_expected_work_log.csv
├─ src/
│  ├─ ingest.py
│  ├─ db.py
│  ├─ ingest_cli.py
│  └─ streamlit_app.py
└─ tests/
   ├─ conftest.py
   ├─ test_ingest.py
   ├─ test_duplicate.py
   ├─ test_ingest_property_like.py
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

本テーマのコードは **セミナー用のローカル検証コード** として作成する。
最短実行用として `db.py` にローカル教材向けの既定値を持つが、環境変数 `RESULTS_DATABASE_URL` が設定されている場合は、その接続先を優先する。

想定接続先:

- PostgreSQL 18.3
- ローカルホスト
- DB 名: `results_record_db`
- ロール名: `results_user`
- パスワード: `results_pass`

`results_pass` はローカル教材専用のデモ用パスワードであり、共有環境や本番環境では使用しない。別環境では、強固な個別認証情報を含む接続URLを `RESULTS_DATABASE_URL` へ設定する。

```bash
export RESULTS_DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME'
```

本実装は恒久運用を前提としない。業務利用する場合は、認証情報の安全な管理、通信暗号化、権限分離、監査、バックアップ等を別途設計する。

#### 実装上の原則

- CLI と Web に業務ロジックを書かない。
- 共通ロジックは `ingest.py` に集約する。
- DB アクセスは `db.py` に集約する。
- Streamlit も `db.py` を通じて PostgreSQL を利用する。
- 入口は分けるが、判定基準は統一する。

### 9.2 `work_sec` 算出の境界条件

**仕様**

- 08:00〜12:00、13:00〜17:00の重複時間だけを積算する。
- 土日と2026-01-12を非稼働日とする。
- 日跨ぎは日ごとに計算し、`end_ts < start_ts` は定義済み補正を除きrejectする。

**解説**

単純な経過時間と勤務時間内の正味作業時間を分けることで、休憩や非稼働時間を含むログも同じ基準で比較できる。

**仕様**

`work_sec` は、`start_ts` から `end_ts` の間に含まれる **稼働時間帯のみ** を積算した秒数とする。  
稼働時間帯は半開区間 `[08:00, 12:00)` と `[13:00, 17:00)` とし、開始境界を含み終了境界を含まない。  
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

**教材コメント**

次の具体例は境界条件を理解するための補助である。実装・テストの合否判定は、直後の仕様として示す期待値を正とする。

**仕様**

以下の期待値は `calc_work_sec` の受入条件とする。

#### 具体例

| start_ts | end_ts | elapsed_sec | work_sec | 理由 |
|---|---|---:|---:|---|
| 2026-01-05 11:50 | 2026-01-05 12:10 | 1200 | 600 | 12:00〜12:10 は昼休みとして控除 |
| 2026-01-05 07:50 | 2026-01-05 08:10 | 1200 | 600 | 08:00 前は非稼働時間として控除 |
| 2026-01-05 16:50 | 2026-01-05 17:10 | 1200 | 600 | 17:00 後は非稼働時間として控除 |
| 2026-01-05 12:10 | 2026-01-05 12:40 | 1800 | 0 | 全時間帯が昼休み |
| 2026-01-05 08:00 | 2026-01-05 09:00 | 3600 | 3600 | 全時間帯が稼働時間内 |
| 2026-01-05 07:30 | 2026-01-05 08:30 | 3600 | 1800 | 08:00前の30分を除外 |
| 2026-01-05 11:30 | 2026-01-05 12:30 | 3600 | 1800 | 12:00以降の30分を昼休みとして除外 |
| 2026-01-05 16:30 | 2026-01-05 17:30 | 3600 | 1800 | 17:00以降の30分を除外 |
| 2026-01-10 08:00 | 2026-01-10 09:00 | 3600 | 0 | 土曜日は非稼働日 |
| 2026-01-12 08:00 | 2026-01-12 09:00 | 3600 | 0 | 固定祝日は非稼働日 |

**仕様**

補足: 本テーマはセミナー向け簡易実装のため、稼働カレンダーは「土日休み + 固定祝日 2026-01-12」のみを扱う。業務時間も `08:00-12:00` / `13:00-17:00` 固定とし、カレンダーマスタ連携は実装しない。


#### KPI1 の 17:00 枠に関する補足

KPI1 は `end_ts` の時間帯（`08:00`〜`17:00`）で件数を集計するため、**17:00 台の完了件数も表示対象**とする。
一方 `work_sec` は稼働時間帯のみを積算するため、`17:00` 以降の時間は算入しない。

- KPI1: 完了時刻ベースの件数
- `work_sec`: 勤務時間内の正味作業時間

このため、17:00 完了枠が表示されても、17:00 以降の作業秒数は `work_sec` へ含めない。

### 9.3 ファイル名からの `worker_name` 抽出規則

**仕様**

- `INTASM_<作業者>_<YYYYMMまたはYYYYMMDD>` を受理する。
- `EXTASM_<作業者>_<YYYYMMまたはYYYYMMDD>` と `EXTASM_<ライン>_<作業者>_<YYYYMMまたはYYYYMMDD>` を受理する。
- 拡張子は `.csv`、`.xlsx`、`.xlsm`、作業者名は日本語も許容する。

**解説**

設備ログに作業者列がない場合、ファイル名が業務情報の一部になる。
規則を明文化し、ファイル名と行データの作業者が両方ある場合は不一致を検出する。

**仕様**

内装組立・外装組立ログでは、`worker_name` はファイル名から抽出する。

加えて、行データ側に `worker_name` 列が存在する場合は、正規化後にファイル名由来の値と一致していることを必須とし、不一致は `INVALID_WORKER_NAME` で reject する。

行データ側の `worker_name` が空白正規化後に空の場合は、ファイル名由来の値を採用し、不一致判定の対象外とする。

標準の内装組立・外装組立CSVは `worker_name` 列を持たない。この判定は、任意の互換列 `worker_name` を含む拡張入力に対する整合性ガードであり、標準サンプルでは発火しない。ファイル名が規則に一致せず作業者名を抽出できない場合は、行単位の `INVALID_WORKER_NAME` ではなく、ファイル単位の入力エラーとして取込を開始しない。

対象パターン:

- `INTASM_YamadaTaro_202601.csv`
- `EXTASM_SatoKen_202601.csv`

正規表現（実装の `FILENAME_WORKER_RE` と同一）:

```text
^(INTASM)_([^_]+)_\d{6}(?:\d{2})?\.(csv|xlsx|xlsm)$
|^(EXTASM)(?:_[^_]+)?_([^_]+)_\d{6}(?:\d{2})?\.(csv|xlsx|xlsm)$
```

抽出規則:

- `INTASM` はグループ 2、`EXTASM` はグループ 5 を `worker_name` とする（英字以外も許容、`_` は除外）。
- `EXTASM` では作業者名の前に任意のライン名を1要素だけ指定できる。

**教材コメント**

例:

- `INTASM_YamadaTaro_202601.csv` → `worker_name = YamadaTaro`
- `EXTASM_SatoKen_202601.csv` → `worker_name = SatoKen`
- `EXTASM_LineA_SatoKen_202601.csv` → `worker_name = SatoKen`

**仕様**

なお、出荷検査ログ（`SHIPCHK_202601.csv`）ではファイル名からは抽出せず、列 `inspector_name` を `worker_name` として使用する。

### 9.3.1 ファイル名プレフィックスによる取込種別判定

`ingest.py` の実装では、取込種別の判定は次のファイル名プレフィックスを正とする。

- `INTASM_...` → `process_name = 内装組立` / `source_system = internal_assembly_tool`
- `EXTASM_...` → `process_name = 外装組立` / `source_system = external_assembly_tool`
- `SHIPCHK_...` → `process_name = 出荷検査` / `source_system = shipping_inspection_tool`

### 9.4 `worker_name` 正規化ルール

**仕様**

- 前後空白、半角空白、全角空白を除去する。
- 漢字とローマ字の自動変換や、英字の大文字・小文字変換は行わない。

**解説**

安全に吸収できる空白差だけを正規化する。
人物同一性の判断が必要な表記差は、辞書や作業者マスタの設計範囲として分離する。

**仕様**

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

**仕様**

- CSV・Excelとも、ヘッダを除いた最初のデータ行を1として保存する。
- 正常行とreject行で同じ数え方を使用する。

**解説**

画面やreject明細から元ファイルの対象行を人が探せるよう、Pythonの0始まりではなく利用者向けの1始まりに統一する。

**仕様**

`source_row_no` は、**CSV / Excel ともに、ヘッダ行を除いたデータ行を 1 始まりで記録する**。  
Excel 取込時も、先頭行をヘッダとして解釈した場合のデータ行番号を記録する。

例:

- ヘッダ直下の最初のデータ行 → `source_row_no = 1`
- 2 行目のデータ行 → `source_row_no = 2`

Python 実装上の 0 始まり index をそのまま記録せず、表示・保存時は 1 始まりへ変換する。

### 9.6 duplicate の扱い

**仕様**

- 重複キーは `(order_no, process_name)` とする。
- 既存DB内と同一ファイル内を事前判定し、競合はDBのUNIQUE制約で最終防衛する。
- 重複行は削除せず `DUPLICATE_KEY` としてrejectへ保存する。

**解説**

再取込で主テーブルの件数を増やさず、どの実行で重複したかを説明可能にする。
本教材では同時実行の厳密なロックまでは扱わない。

**仕様**

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

**仕様**

- 通常の自動テストはSQLiteインメモリDBで、変換・reject・重複・KPIを高速に確認する。
- PostgreSQLではDDL、型、接続、正常6ファイル取込、Streamlit表示を別途結合確認する。
- 入力に対する登録件数、reject件数、理由コード、正規化値、KPI集計値を固定して比較する。

**解説**

SQLiteとPostgreSQLには型・DDL・ドライバ差があるため、単一のテスト環境ですべてを代替しない。
ロジック回帰と実環境確認を二層に分けることで、短時間の自動テストと本番DB相当の確認を両立する。

**仕様**

本節では、本教材で最低限確認するテスト観点と受入条件を定義する。  
あわせて、セミナー用モデルとして扱う品質の範囲と、実運用へ展開する場合に必要となる品質要求を整理する。

テストの目的は、単にコードが実行できることを確認することではない。  
**実装結果が、文書化した業務ルール、仕様、制約、受入条件と一致していることを確認する**ことにある。

#### 9.7.1 本教材で固定するテスト観点

サンプルデータを用いて、以下のテスト観点を確認する。

| 分類 | テスト観点 | 期待値 |
|---|---|---|
| 正常系 | 正常データ取込 | 正常行が `work_log` に登録され、主要項目が期待する正規化結果と一致する |
| 入力検証 | 必須項目の欠損 | `work_log` には登録されず、`work_log_reject` に `MISSING_REQUIRED` として記録される |
| 入力検証 | 日時変換失敗 | `work_log` には登録されず、`work_log_reject` に `DATE_PARSE_ERROR` として記録される |
| 時系列整合性 | `end_ts < start_ts` | 仕様上の補正対象を除き、`work_log_reject` に `END_BEFORE_START` として記録される |
| エラー行 | 元ログにエラーコードが存在する | `work_log` には登録されず、`work_log_reject` に対応する理由コードが記録される |
| マスタ整合性 | 補助マスタに対象製番が存在しない | `work_log` には登録されず、`work_log_reject` に `MASTER_NOT_FOUND` として記録される |
| 再実行性・重複制御 | 同一データの再取込 | `work_log` の件数は増加せず、重複行が `work_log_reject` に `DUPLICATE_KEY` として記録される |
| 監査性 | 同一ファイルの再取込 | 取込実行ごとに異なる `ingest_batch_id` が発行され、どの実行で reject が発生したか追跡できる |
| KPI 1 | 工程別時間別の作業台数 | サンプルデータから算出した工程別・時間別件数が、固定した期待値と一致する |
| KPI 2 | 工程間滞留 | 指定した評価時刻における工程間滞留件数が、固定した期待値と一致する |
| KPI 3 | 作業者別日別実績 | 作業者・工程・日付ごとの作業台数が、固定した期待値と一致する |

`end_ts < start_ts` の扱いについては、すべてを一律に reject するわけではない。  
出荷検査ログの翌営業日補正を適用する場合は、補正後の値が期待結果と一致することを確認する。

#### 9.7.2 セミナー用の最低受入条件

本教材では、セミナー時間内に設計から実装、取込、可視化までの流れを説明するため、最低受入条件を以下に絞る。

- 正常データが `work_log` に登録されること
- 不正データが正常データと分離され、理由付きで `work_log_reject` に記録されること
- 同一データを再投入しても `work_log` の件数が増えないこと
- KPI 3種が定義した条件で算出され、Streamlit 上で描画できること
- 取込実行と reject の関係を `ingest_batch_id` で追跡できること

単に「画面が表示された」「グラフが描画された」だけでは、計算結果の正しさまでは確認できない。  
厳密なテストでは、入力データに対する登録件数、reject件数、理由コード、正規化結果、KPI集計値を期待値として固定し、実行結果と比較する。

期待値は、例えば以下のような別ファイルとして保持できる。

- `sample_expected_work_log.csv`
- KPIごとの期待集計結果CSV
- reject行と理由コードの期待結果
- 指定時刻における工程間滞留件数

本READMEでは、まず「何を確認するか」を固定する。  
実装段階では、それぞれの期待値をテストデータとして具体化する。

#### 9.7.3 テスト環境の方針

本教材では、目的の異なる次の2層で確認する。

1. **通常の自動テスト**: SQLAlchemyを介してSQLiteインメモリDBを使用し、変換、reject、重複防止、KPI集計を高速かつ再現可能に確認する。
2. **PostgreSQL結合確認**: 教材のDDLとローカルPostgreSQLを使用し、PostgreSQL固有の型・制約、接続、正常ファイルの取込、Streamlit表示までを確認する。

自動テストでDB処理を単純なモックに置き換えず、SQLAlchemyからDBへ至る経路を通す。ただし、日常的な回帰テストを特定のローカルPostgreSQL環境へ依存させない。

#### 9.7.3.1 Pull Request時の自動テスト

- GitHub Actions の `.github/workflows/results-record-db-tests.yml` を使用し、すべての Pull Request で自動テストを実行する。
- Python 3.11 と `results_record_db/requirements.txt` を基準環境とする。
- `results_record_db` を作業ディレクトリとして `python -m pytest -q` を実行する。
- CIではSQLiteインメモリDBによる通常の自動テストを対象とし、PostgreSQL結合確認は別途実施する。
- 自動テストが失敗したPull Requestは、原因を確認してからマージする。

AIにテスト実装を依頼する際は、以下を明記する。

- 通常の自動テストにはSQLiteインメモリDBを使用する
- DB登録処理を単純なモックへ置き換えない
- テスト開始前のデータ状態を明確にする
- PostgreSQL結合確認では、対象テーブルに既存データがある場合はテスト開始前に初期化し、テストで作成したデータはテスト終了後に削除する
- テスト結果が既存データの有無に左右されないようにする
- 同一テストを繰り返しても、結果が変化しないようにする

ここで確認したいのは、個々の関数だけではなく、以下を含む一連の処理である。

```text
入力ファイル
  ↓
列名マッピング
  ↓
型変換・正規化
  ↓
入力検証・reject判定
  ↓
PostgreSQLへの登録
  ↓
KPI集計
```

このため、本教材のテストには単体テストだけでなく、複数の処理をつないで確認する結合テストの性格も含まれる。

#### 9.7.4 本教材におけるテストの範囲

ソフトウェア品質は、それだけで独立したセミナーが成立するほど広い領域である。  
本教材では、すべての品質観点を網羅することは目的としない。

主に扱うのは、以下の範囲である。

- 機能要件が実装へ正しく反映されていること
- 正常データと異常データを期待どおりに分離できること
- 同一データの再投入に対して、データ整合性を維持できること
- KPIの計算結果が、定義した期待値と一致すること
- 取込結果とエラー理由を追跡できること

テストシナリオは、実装後に追加するのではなく、要求、仕様、受入条件とあわせて設計段階で定義することが望ましい。

テスト設計に不慣れな場合は、機能要件や受入条件をAIへ渡し、以下の観点を洗い出す方法も有効である。

- 正常系
- 境界値
- 必須項目の欠損
- 型・形式の不正
- 時系列の矛盾
- 重複投入
- 再実行
- データなし
- DB接続失敗
- 想定外の列や入力形式
- 複数利用者による同時操作

ただし、AIが挙げたテスト観点が十分であるとは限らない。  
業務上の影響、障害時の挙動、運用手順を理解した人間が、観点の不足や優先順位を確認する必要がある。

#### 9.7.5 利用目的別の品質要求

必要な品質水準は、ソフトウェアの利用目的、利用人数、障害時の影響、運用期間によって異なる。

以下は、一般規格に基づく正式な分類や成熟度モデルではない。  
本教材で、利用目的と品質要求の関係を説明するための便宜的な分類である。

また、レベルが高いほど常に優れているという意味ではない。  
用途に対して必要十分な品質水準を設定することが重要である。

| レベル | グレード名 | 主な用途 | 品質の考え方 | 代表的な要求 |
|---:|---|---|---|---|
| 1 | 実験・ホビー品質 | 個人開発、学習、技術検証、使い捨てスクリプト | まず仮説を試し、動作を確認することを優先する | 最低限の動作確認、簡単なコメント、実行手順、自分が理解できる構成 |
| 2 | 便利ツール品質 | 社内ツール、小規模自動化、チーム内補助ツール | 限定された利用者が、問題発生時に手動で復旧できることを重視する | 基本的な入力検証、エラー処理、README、設定値の外出し、ログ、バックアップ、手動復旧手順 |
| 3 | 業務・プロダクト品質 | 業務アプリ、Webサービス、SaaS、顧客向けアプリ | 継続的に運用・保守・変更でき、利用者や管理者へ説明できることを重視する | 自動テスト、CI/CD、コードレビュー、認証・認可、監視、構造化ログ、脆弱性対策、データ整合性、変更管理 |
| 4 | ミッションクリティカル品質 | 24時間365日稼働、金融・決済、物流、通信、大規模基盤、重要な組込み | 一部に障害が発生しても、重要な業務やサービス全体が破綻しないことを重視する | 冗長化、フェイルオーバー、縮退運転、SLO/SLA、負荷試験、監視・通知、障害対応手順、バックアップ、復旧訓練、監査ログ |
| 5 | 安全・規制・社会インフラ品質 | 航空、鉄道、医療機器、プラント、電力制御、防衛、宇宙 | 失敗が人命、社会機能、環境、巨大資産へ影響する前提で、証明可能性と監査性を重視する | 規格準拠、形式的検証、独立レビュー、要件トレーサビリティ、安全解析、厳格な変更管理、再現可能ビルド、構成管理、長期保守 |

今回の題材が実運用される場合に目指す品質水準は、概ねレベル3「**業務・プロダクト品質**」に相当する。

一方で、本リポジトリの実装は、実運用システムを完成させることではなく、DocDDによる設計・実装・検証の流れを説明するためのセミナー教材である。  
そのため、教材としての実装範囲は、**レベル2「便利ツール品質」相当を最低要求**としている。

これは、品質を軽視するという意味ではない。  
目的に対して説明上の優先度が低い機能を省略し、以下の点に重点を置くためである。

- 文書から実装へつながること
- 代表的な異常系を扱えること
- 重複やデータ不整合を防止できること
- 受入条件をテストで確認できること
- 実運用へ発展させる際の不足要件を説明できること

#### 9.7.6 品質要求と開発コスト

AIを用いた開発であっても、品質要求が自動的に満たされるわけではない。

品質要求を高めるほど、以下に必要な設計・実装・確認作業も増加する。

- 要件定義
- 例外処理
- テスト設計
- テストデータ作成
- コードレビュー
- セキュリティ対策
- 監視・ログ
- 障害復旧
- ドキュメント
- 継続的な保守

したがって、品質要求は、設計工数、実装工数、試験工数、運用コストに直結する。

例えば、限定された利用者が使う補助ツールに、金融決済システムと同じ可用性や監査性を要求することは、通常は適切ではない。  
反対に、重要な業務で使うシステムを、試作ツールと同じ品質水準で運用することも適切ではない。

DocDDでは、品質を一律に最大化するのではなく、用途とリスクに応じた品質要求を文書として明示する。

#### 9.7.7 AIコーディングにおける品質向上

AIコーディングを利用する場合も、一般的な開発と同様に、以下の流れが必要である。

1. 利用目的と想定利用者を明示する
2. 機能要件と非機能要件を整理する
3. 受入条件とテスト観点を定義する
4. AIへ実装を依頼する
5. 生成されたコードと差分をレビューする
6. テストを実行し、期待値と比較する
7. 問題があれば、仕様または実装を修正する
8. 変更内容を文書へ反映する

AIに複数の実装案を提示させ、それぞれの長所、短所、障害時の挙動を比較する方法も有効である。

また、実装を担当したAIとは別のAIサービスへコードレビューを依頼し、異なる観点から指摘を得る方法も利用できる。  
例えば、次のような観点を分けて確認できる。

- 仕様との整合性
- 例外処理
- データ整合性
- セキュリティ
- 性能
- 保守性
- テスト不足
- ログと監査性

ただし、複数のAIが同じ結論を出したことは、実装の正しさを保証しない。  
AIによるクロスレビューは、観点を増やすための補助的な手段であり、最終的な採否判断と品質責任は人間側に残る。

#### 9.7.8 非機能要件・例外処理・セキュリティ

機能要件は「何ができるか」を定義する。  
一方、非機能要件は「どのような条件で、どの程度の品質で動作するか」を定義する。

代表的な非機能要件には、以下がある。

- 性能
- 可用性
- 信頼性
- セキュリティ
- 保守性
- 運用性
- 監査性
- バックアップと復旧
- 障害時の振る舞い
- 利用環境と対応期間

例外処理は、機能要件だけから自動的に決まるものではない。

例えば、データ整合性を優先する業務アプリでは、不正な入力やDB登録失敗が発生した場合に、その処理を中断し、理由を記録して再投入を求める設計が適切な場合がある。

一方、ミッションクリティカルなシステムでは、単純に処理を継続するか停止するかだけではなく、以下のような障害時の振る舞いを事前に定義する必要がある。

- 安全側停止
- 縮退運転
- 問題が発生した処理単位の隔離
- フェイルオーバー
- 再試行
- 手動運転への切替
- 復旧後の再処理
- 利用者や管理者への通知

セキュリティについても同様である。

AIへ「安全なシステムを作成する」とだけ指示しても、必要な対策は一意に決まらない。  
少なくとも、以下のような条件を文書で明示する必要がある。

- 誰が利用できるか
- 誰がデータを閲覧・登録・変更できるか
- 認証情報やDB接続情報をどこに保持するか
- 操作履歴をどこまで記録するか
- 個人情報や機密情報を扱うか
- 外部公開するか、社内ネットワークに限定するか
- 脆弱性や依存ライブラリをどのように管理するか
- 障害や不正アクセスを誰へ通知するか

これらの条件は、設計書や非機能要件として明示しない限り、AIが業務上適切な優先順位を判断することは難しい。

#### 9.7.9 KPIの計算テストと業務妥当性

KPIについては、次の2つを分けて確認する必要がある。

1. **計算ロジックの正しさ**  
   固定した入力データに対して、プログラムが期待する集計値を返すこと。

2. **KPI定義の業務上の妥当性**  
   その集計方法や数値が、実際の現場状態と対応していること。

前者は、期待値を固定した自動テストや手計算との照合によって確認できる。  
後者は、システム上のデータだけでは十分に確認できない場合がある。

例えば工程間滞留では、指定時刻に現場の仕掛り品を実測し、システム上の計算値と比較する方法がある。  
差異が生じた場合は、計算式の誤りだけでなく、記録時刻のずれ、工程外滞留、手直し、搬送待ち、ログ欠落、現場とシステムでの「仕掛り」の定義差を確認する。

KPI定義と現場実測による妥当性確認については、  
[9.8.4 KPI定義と評価ロジックの妥当性](#984-kpi定義と評価ロジックの妥当性)で扱う。


### 9.8 Streamlit 画面仕様（開発初期指示と最終仕様）

**仕様**

- Import、KPI1、KPI2、KPI3の4タブを提供する。
- 期間・工程・作業者フィルタ、グラフ、詳細表、CSV出力を提供する。
- KPI2は前工程完了から次工程開始までの未着手件数を15分粒度で表示する。

**解説**

開発初期指示と最終仕様を併記することで、文書から実装へ具体化する過程を示す。
KPI2は工程間待ちと次工程内作業を混在させない。

**教材コメント**

Streamlit画面は、利用者が実際に見て理解しやすいかを確認しながら改善する領域である。本教材では、初期表示項目と最低限の確認条件を定め、実装後にトライアンドエラーで見せ方を改善する過程も学習対象に含める。ただし、画面改善によってKPIの意味を変更してはならない。

**仕様**

- データ処理、KPIの計算定義、出力元データ、集計粒度は画面改善の対象外とし、本節の仕様どおりに固定する。
- 色、余白、説明文、グラフの高さは、KPIの値、フィルタ条件、CSV出力内容を変更しない範囲で変更を許容する。
- タブ構成、フィルタの意味、0件時の挙動、CSVファイル名を変更する場合は、実装変更と同時に本節の最終仕様を更新する。

**仕様**

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
  - `UNIQUE (order_no, process_name)` により、同一製番・同一工程の実績は1件に固定。
  - 前工程の `end_ts` から次工程の `start_ts` までを工程間滞留として評価。
  - `to_start < from_end` は監査情報として保持しつつ、推移カウントから除外。
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
- 滞留件数は「`from_end <= ts` かつ `to_start` が未開始または `to_start > ts`」でカウント。
- `UNIQUE (order_no, process_name)` により、同一 `order_no`・同一工程の実績は1件に固定する。
  - `to_start < from_end` は `is_invalid_sequence=True` として明細に残す。
  - ただし滞留推移カウントには invalid sequence 行を使わない。
- 出力は推移（折れ線）と明細（表）を分け、CSV は以下の2種類。
  - `kpi2_stagnation_trend.csv`
  - `kpi2_stagnation_detail.csv`

KPI1とKPI2の時間窓は、評価対象が異なるため一致させない。KPI1は完了イベントを時刻の「時」で集計し、`17:00 <= end_ts < 18:00` の完了イベントを17:00枠へ含める。KPI2は稼働時間内の状態を15分間隔の評価時点で観測し、半開区間 `[08:00, 17:00)` を使用するため、最終評価時点は16:45となり17:00は含めない。

#### KPI3（作業者別日別実績）

- 集計条件は「期間・工程・作業者」で絞り込み。
- 集計単位は `work_date × process_name × worker_name` の件数。
- 画面上はさらに工程を単一選択して、作業者別棒グラフ（日付色分け）を表示。
- CSV ダウンロード名は `kpi3_worker_daily.csv`。

#### エラー/空データ時の挙動

- DB読み込み失敗・必須列不足時はエラー表示し、空DataFrameとして継続。
- 表示対象データが空の場合は警告を表示し、フィルタ・タブUIは維持する。
- Streamlit 実行コンテキスト外（例: `python streamlit_app.py` による直接実行）では、ガイダンス文を標準出力して終了する。

#### 画面表示例
上記の設計にてStreamlitで画面表示をおこなった際の実装例は下記となる。

<img width="2980" height="600" alt="output" src="https://github.com/user-attachments/assets/aae3932e-c32a-4a7c-93fa-0cd7e1345c17" />

**教材コメント**

グラフに使用する色のルールを設ける場合は、対象要素、色コード、色の意味をドキュメントに明示すると、UI/UXの説明がわかりやすくなる。

**仕様**

#### 9.8.4 KPI定義と評価ロジックの妥当性

KPI画面では、グラフが表示されること自体よりも、  
**そのKPIが業務上の意味と一致しているか** が重要である。

特に KPI2「工程間滞留」は、単にSQLやPythonで件数を数えればよいものではない。  
まず、業務上の「仕掛り」または「工程間滞留」をどう定義するかを固定する必要がある。

本テーマでは、工程間滞留を以下のように定義する。

| 区間 | 滞留として数える状態 |
|---|---|
| 内装組立 → 外装組立 | 内装組立が完了済みで、外装組立が未着手 |
| 外装組立 → 出荷検査 | 外装組立が完了済みで、出荷検査が未着手 |

時点 `ts` における滞留判定は、以下の条件で行う。

```text
from_end <= ts
かつ
to_start が存在しない、または to_start > ts
```

つまり、前工程が終わっていて、後工程がまだ始まっていない状態を、
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
| 集計粒度 | 日別・時間別・15分足のいずれを採用するか |

したがって、KPIの妥当性はコードだけでは担保できない。  
以下の順で担保する。

1. 業務上のKPI定義を文書化する
2. 計算ロジックを仕様として明記する
3. 代表的な製番・工程データを使って期待値を作る
4. 手計算または既存管理表と突合する
5. 現場実測データを取得できる場合は、システム計算値と実測値を並行評価する
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
| 時刻別サンプリング | 評価時刻を事前に固定し（例: 10:00、13:00、15:00）、各時刻の実測値とシステム計算値を比較する |
| 写真・現場記録との照合 | 置き場写真または現場記録を取得している場合は、その記録とシステム計算値を照合する |

このとき重要なのは、システム計算値と現場実測値が完全一致することだけを目的にしないことである。  
差異が出た場合は、以下のどれに該当するかを確認する。

| 差異の原因 | 例 |
|---|---|
| KPI定義の違い | 現場は「置き場にある数」を数えているが、システムは「後工程未完了数」を数えている |
| 記録タイミングの違い | 実際の作業完了と、ログ記録時刻にズレがある |
| 工程外の滞留 | 工程定義に含まれない待ち状態（例: 検査待ち、手直し待ち、搬送待ち）が存在する |
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

**仕様**

- README、DDL、ORM、取込、画面、テストの定義を同期する。
- 不明点を一般論で補完せず、仕様へ戻して判断する。
- 変更時は関連するサンプルと期待値も更新する。

**解説**

DocDDではコード生成の速さより、判断の根拠と成果物間の整合性を重視する。
一つの修正がどの文書・コード・テストへ影響するかを追跡する。

**仕様**

本テーマでは、AI にコードを起こさせるが、以下を原則とする。

- 先に README の文書を固める。
- 生成されたコードはそのまま採用せず、必ずレビューする。
- 論点は「1発で生成できるか」ではなく「仕様どおりか」。
- 実行デモは事前検証済み版で行う。

このため、AI に渡すプロンプトでは「コードを書け」ではなく、  
**この README に従って DDL / 取込処理 / Streamlit UI を作成せよ** という形で、文書を一次情報として扱う。


---

## 10. アーキテクチャ図

**仕様**

- 入力、共通取込、DB、KPI表示の責務とデータの流れを図示する。
- 図中のファイル名、工程順、使用時刻を現行実装と一致させる。

**解説**

表だけでは分かりにくい入口の違い、処理の共通化、正常・reject分岐、KPIへの接続を視覚的に説明する。

**仕様**

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

**仕様**

- CLIとWebUIは同じ `src/ingest.py` を呼び出す。
- 入力経路に業務判定を重複実装しない。

**解説**

入口は利用場面に応じて分けるが、正常・異常の判断基準は一つに保つ。

**仕様**

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

**仕様**

- 図の各責務を `db.py`、`ingest.py`、`ingest_cli.py`、`streamlit_app.py`、`tests/` に対応付ける。

**解説**

設計上の箱と実際のファイルを対応させることで、初学者が修正対象を見つけやすくする。

**仕様**

| 層 | 主な役割 | 想定ファイル |
|---|---|---|
| 入口（CLI） | ファイルパスや入力元を受け取り、共通取込処理を呼ぶ | `src/ingest_cli.py` |
| 入口（Web） | アップロードファイルを受け取り、共通取込処理を呼ぶ | `src/streamlit_app.py` |
| 共通取込処理 | 列マッピング、型変換、必須チェック、値域チェック、reject 判定、DB 登録 | `src/ingest.py` |
| DB 層 | SQLAlchemy による接続、モデル定義、セッション管理 | `src/db.py` |
| 表示層 | KPI 集計、グラフ表示、CSV 出力 | `src/streamlit_app.py` |

補足: 本テーマはセミナー題材のため、責務を明確にしつつ、過度なファイル分割は行わない。


### 10.3 業務工程の流れ

**仕様**

- 内装組立 → 外装組立 → 出荷検査の固定順を示す。
- KPI2は前工程の `end_ts` と次工程の `start_ts` を接続して表現する。

**解説**

ログの取込順ではなく、業務工程順と実績時刻から状態を評価する。
次工程開始後は工程間滞留ではなく工程内作業として扱う。

**仕様**

本テーマで扱う業務上の工程は、BOP として **内装組立 → 外装組立 → 出荷検査** の固定順とする。  
各工程は別々のツール・帳票からログを出力するが、`order_no` をキーに同一製番の工程進捗として結び付ける。

```mermaid
flowchart LR
    order["受注 / 製番発行<br/>order_no"] --> internal["内装組立<br/>設備生ログ<br/>INTASM_*.csv"]
    internal --> external["外装組立<br/>実績ログ<br/>EXTASM_*.csv"]
    external --> inspection["出荷検査<br/>検査ログ<br/>SHIPCHK_*.csv"]
    inspection --> shipped["出荷可能状態"]

    internal -. 完了時刻 end_ts .-> kpi2a["工程間滞留<br/>内装 → 外装"]
    external -. 開始時刻 start_ts .-> kpi2a
    external -. 完了時刻 end_ts .-> kpi2b["工程間滞留<br/>外装 → 出荷"]
    inspection -. 開始時刻 start_ts .-> kpi2b
```

この図で重要なのは、ログの入力順ではなく、**業務上の工程順**と、前工程の完了時刻 `end_ts`・次工程の開始時刻 `start_ts` を基準に KPI を評価する点である。
特に KPI2 は、前工程が完了し、次工程が未開始の時間帯を工程間滞留として数える。

### 10.4 CLI/WebUI から見える状態までの流れ

**仕様**

- ファイル受領から検証、正常・reject分岐、DB保存、KPI表示までを一連で示す。
- WebUIはプレビュー後、登録直前にも同じアップロード内容を再検証する。

**解説**

利用者が見る画面の背後で、どの共通処理とテーブルを通っているかを説明する図である。

**仕様**

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

**仕様**

- 本文で使用する業務・データ・実装用語を、教材内で一貫した意味に定義する。
- 初出時に理解しづらい略語や英語表現を補足する。

**解説**

同じ言葉を参加者ごとに異なる意味で理解すると、仕様合意が崩れる。
用語集は技術用語の翻訳だけでなく、本教材における判断基準を共有する役割を持つ。

**仕様**

本テーマで使う用語を以下に整理する。

| 用語 | 意味 |
|---|---|
| 業務モデル | 何を単位に記録し、工程がどう流れるか、何を 1 レコードとみなすかを定義したもの |
| KPI | 最終的に見たい評価指標。本テーマでは「工程別時間別の作業台数」「工程間滞留」「作業者ごとの日別作業台数」の 3 種 |
| 正規化 | 異なる元ログを、共通の意味を持つカラムへ揃えて取り込める形にすること |
| `work_log` | 正常に取り込まれた作業実績を保持する主テーブル |
| `work_log_reject` | 取り込めなかった行を、理由付きで保持する reject テーブル |
| reject | 入力不正または制約違反により、主テーブルへ登録せず別管理すること |
| データコントラクト | 何を正しいデータとみなすかを定義した合意。本テーマでは、列、型、同一判定、例外条件を含む |
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

**仕様**

- データコントラクト、受入条件、運用ガードレールを、実装・テスト・運用へ結び付けて説明する。

**解説**

DocDDで重要なのは文書量ではなく、何を正とし、何をもって完成とし、誰がどう運用するかを固定することである。

**仕様**

#### データコントラクト

「何を正とみなすか」を固定するための定義。  
本テーマでは、列・型・UNIQUE・CHECK・reject 条件・正規化ルールがここに含まれる。

#### 受入条件

「何をもって完成とするか」を固定するための定義。  
本テーマでは、reject が正しく記録されること、重複で件数が増えないこと、KPI 3 種が描画できることが最低条件となる。

#### 運用ガードレール

「誰がどう回すか」を固定するための定義。  
本テーマでは、CLI / Web の入口を分けつつロジックは共通化すること、ローカル PostgreSQL で検証できること、デモは事前検証済み版で行うことが相当する。
