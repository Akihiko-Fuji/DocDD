# results_record_db — Quick Start & AI プロンプト例

> **目的**  
> `results_record_db` テーマを短時間で把握し、最小手順で動かし始めるための **Quick Start** と、AI に実装を依頼する際の **プロンプト例** をまとめたドキュメント。  
>
> 本テーマでは README を一次情報として扱い、  
> **文書 → DDL → DB → 取込処理 → テスト → Streamlit 可視化**  
> の順で進めることを前提とする。

---

## 目次

1. [Quick Start](#1-quick-start)  
   1.1 [この題材で何を作るのか](#11-この題材で何を作るのか)  
   1.2 [最初に読むファイル](#12-最初に読むファイル)  
   1.3 [最短実行手順](#13-最短実行手順)  
   1.4 [実装ファイルの最小構成](#14-実装ファイルの最小構成)  
   1.5 [この題材での実装原則](#15-この題材での実装原則)  
2. [AI に渡すプロンプト例](#2-ai-に渡すプロンプト例)  
   2.1 [DDL 作成用](#21-ddl-作成用プロンプト)  
   2.2 [SQLAlchemy モデル作成用](#22-sqlalchemy-モデル作成用プロンプト)  
   2.3 [共通取込処理作成用](#23-共通取込処理作成用プロンプト)  
   2.4 [CLI 入口作成用](#24-cli-入口作成用プロンプト)  
   2.5 [Streamlit 作成用](#25-streamlit-作成用プロンプト)  
   2.6 [テスト作成用](#26-テスト作成用プロンプト)  
3. [使い方のコツ](#3-使い方のコツ)  
4. [このファイルの位置づけ](#4-このファイルの位置づけ)

---

## 1. Quick Start

### 1.1 この題材で何を作るのか

異なる **3 種類の元ログ** を共通ルールで正規化し、PostgreSQL に取り込み、Streamlit で KPI を可視化するシステムを構築する。

**対象工程**

| # | 工程 |
|---|------|
| 1 | 内装組立 |
| 2 | 外装組立 |
| 3 | 出荷検査 |

**確認したい KPI**

| # | KPI |
|---|-----|
| 1 | 工程別・時間別の作業台数 |
| 2 | 工程間滞留 |
| 3 | 作業者ごとの日別作業台数 |

---

### 1.2 最初に読むファイル

実装を始める前に、以下の 2 ファイルを必ず読むこと。

| ファイル | 目的 |
|----------|------|
| `results_record_db/README.md` | 業務モデル・DB 設計・取込方針・画面要件の把握 |
| `results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md` | ローカル PostgreSQL の準備方法の確認 |

---

### 1.3 最短実行手順

> ここでは「まず動かす」ことを優先し、**CLI で CSV を取り込んでから Streamlit を開く**までを最短で実施する。
WindowsでPythonやライブラリの準備から行う場合は、先に [`WINDOWS_SETUP.md`](./WINDOWS_SETUP.md) を参照してください。

#### 1.3.0 非エンジニア向けの用語メモ

- **CSV**: Excel で開ける表形式ファイル
- **CLI**: 黒い画面（ターミナル）でコマンドを実行する方法
- **DB (PostgreSQL)**: データを保存する箱
- **DDL**: DB のテーブル定義を作る SQL ファイル
- **Streamlit**: ブラウザでダッシュボードを表示する Python ツール

> まずは「コマンドを上から順にコピーして実行」すれば OK。
> 細かい意味は後から追って理解すれば問題ない。

#### Step 1 — PostgreSQL を準備する

- PostgreSQL 18.3 をローカルへ導入する
- ロール `results_user` を作成する
- DB `results_record_db` を作成する
- `results_record_db/ddl/ddl_results_record_db.sql` を `psql` で適用する

実行例:

```bash
psql -U results_user -d results_record_db -f results_record_db/ddl/ddl_results_record_db.sql
```

#### Step 2 — Python 実行環境を準備する

Python 3.11以上を使用する。`results_record_db` 配下で仮想環境を作成し、
依存は `requirements.txt` からまとめて導入する。

```bash
cd results_record_db
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

#### Step 3 — Python ファイルの役割を把握する

最短実行で使う主要ファイルは以下。

- `src/db.py`:
  - PostgreSQL 接続設定
  - SQLAlchemy のエンジン/セッション
  - `work_log`, `work_log_reject` のモデル定義
- `src/ingest.py`:
  - 各 CSV の読込
  - 共通スキーマへの正規化
  - `work_log` への登録
  - 異常データ/重複の `work_log_reject` 登録
- `src/ingest_cli.py`:
  - CLI から対象 CSV を指定して取込を実行する入口
- `src/streamlit_app.py`:
  - KPI 可視化画面（フィルタ、集計、CSV 出力）

#### Step 4 — CLI で対象ファイルをアップロード（取込）する

まずは sample_data の標準 6 ファイルを順に取り込む。

```bash
python src/ingest_cli.py sample_data/INTASM_HanaYamada_202601.csv --order-product-master sample_data/order_product_master.csv
python src/ingest_cli.py sample_data/INTASM_KentoTakahashi_202601.csv --order-product-master sample_data/order_product_master.csv
python src/ingest_cli.py sample_data/EXTASM_MunekiYoshimura_202601.csv
python src/ingest_cli.py sample_data/EXTASM_ToshioAndo_202601.csv
python src/ingest_cli.py sample_data/EXTASM_ShuheiYamashita_202601.csv
python src/ingest_cli.py sample_data/SHIPCHK_202601.csv
```

異常データの動きも見たい場合は、次の3ファイルを同様に実行する。

- `sample_data/INTASM_HanaYamadaInvalid_202601.csv`
- `sample_data/EXTASM_MunekiYoshimuraInvalid_202601.csv`
- `sample_data/SHIPCHK_202601_invalid.csv`

invalid サンプルはデモ説明しやすいよう、**1行1不正** で作成している。各レコードの意図は次のとおり。

- `INTASM_HanaYamadaInvalid_202601.csv`

| 行 | 不正内容 | 想定 reject 理由 |
|---:|---|---|
| 1 | `end_time < start_time`（order_no はマスタ存在） | `END_BEFORE_START` |
| 2 | `start_marker=BEGIN` | `MISSING_REQUIRED` |
| 3 | `end_marker=FIN` | `MISSING_REQUIRED` |
| 4 | `order_no` 空 | `MISSING_REQUIRED` |
| 5 | マスタ未登録 `order_no` | `MASTER_NOT_FOUND` |
| 6 | 既存正常データと同一キー（`order_no`,`process_name`） | `DUPLICATE_KEY` |

- `EXTASM_MunekiYoshimuraInvalid_202601.csv`

| 行 | 不正内容 | 想定 reject 理由 |
|---:|---|---|
| 1 | `error_code` 非空 | `ERROR_CODE_PRESENT` |
| 2 | `error_code` 空 + `all_clear_ts < qr_read_ts` | `END_BEFORE_START` |
| 3 | `order_no` 空 | `MISSING_REQUIRED` |
| 4 | `qr_read_ts` 形式不正 | `DATE_PARSE_ERROR` |
| 5 | `product_name` 空 | `MISSING_REQUIRED` |

- `SHIPCHK_202601_invalid.csv`

| 行 | 不正内容 | 想定 reject 理由 |
|---:|---|---|
| 1 | `inspector_name` 空 | `MISSING_REQUIRED` |
| 2 | `order_no` 空 | `MISSING_REQUIRED` |
| 3 | `inspection_date` 形式不正 | `DATE_PARSE_ERROR` |
| 4 | `start_time` 形式不正 | `DATE_PARSE_ERROR` |
| 5 | `ng_total` 非数値 | `INVALID_RESULT_CD` |

> 注記: CLI はファイル名規約（`INTASM_*` / `EXTASM_*` / `SHIPCHK_*`）で取込種別を判定するため、Quick Start では正規ファイル名を利用する。

#### Step 5 — 最低限のテストを行う

`results_record_db` 配下で pytest を実行する。

```bash
pytest -q
```

最低限確認したいポイント（うまくいっているサイン）:

- 正常取込
- reject
- duplicate
- KPI 集計可能性

#### Step 6 — Streamlit を起動してブラウザで開く

Streamlit を起動する。

```bash
streamlit run src/streamlit_app.py
```

起動後の表示例:

- `Local URL: http://localhost:8501`
- `Network URL: http://<your-ip>:8501`

ブラウザで `http://localhost:8501` を開く。  
画面が表示されれば起動成功。Import タブで「アップロード → 検証・プレビュー → DBへ登録」を実行し、次に期間・工程・作業者を選択して KPI 3 種と CSV 出力を確認する。

> 注記: Streamlit の Web 取込はセミナー向けに **単一ファイルずつ** の運用を前提としている。複数ファイルを一括で取り込む場合は CLI を利用する。

---

### 1.4 実装ファイルの最小構成

```text
results_record_db/
├── README.md
├── results_record_db_LOCAL_POSTGRESQL_SETUP.md
├── ddl/
│   └── ddl_results_record_db.sql
├── sample_data/
├── src/
│   ├── ingest.py          # 共通取込処理
│   ├── db.py              # DB 接続・モデル定義
│   ├── ingest_cli.py      # CLI 入口
│   └── streamlit_app.py   # Streamlit UI
└── tests/
    ├── test_ingest.py
    ├── test_duplicate.py
    └── test_kpi.py
```

---

### 1.5 この題材での実装原則

| 原則 | 内容 |
|------|------|
| CLI と Web は入口だけにする | 業務ロジックを入口に書かない |
| 共通化する | 判定・変換・reject 判定・DB 登録は共通関数に集約する |
| DB 層を一元化する | DB 接続とモデル定義は SQLAlchemy で一本化する |
| DB 接続情報は固定化する | 本テーマでは `db.py` に接続情報をハードコードする（セミナー用ローカル検証前提） |
| Streamlit も同じ DB 層を使う | Streamlit 側には業務取込ロジックを書かない。表示用 SQL は最小限に留める |
| 論点を「仕様どおりか」に置く | 「1 発で生成できるか」ではなく仕様適合を重視する |

---

## 2. AI に渡すプロンプト例

> README を一次情報として AI に実装を依頼するためのプロンプト例。  
> そのまま使っても、必要に応じて調整してもよい。

---

### 2.1 DDL 作成用プロンプト

```
あなたは PostgreSQL 18.3 向けの DDL を作成するエンジニアです。
`results_record_db/README.md` を一次情報（source of truth）として扱い、
本テーマ用の DDL ファイル `ddl_results_record_db.sql` を作成してください。

## 目的

- `work_log`
- `work_log_reject`

の 2 テーブルを、README の定義どおりに PostgreSQL 18.3 向け DDL として作成する。

## 最重要ルール

- README を唯一の正とし、一般論で仕様を補わない
- README に明示されていない要件を勝手に追加しない
- 迷った場合は「README に書かれている内容を優先」する
- 今回はセミナー用ローカル検証が目的なので、過度な汎用化をしない

## 必須要件

- PostgreSQL 方言で記述する
- 出力ファイル名は `ddl_results_record_db.sql` を想定する
- 作成対象は `work_log` と `work_log_reject` の 2 テーブルのみとする
- `work_log_id`, `reject_id` は `BIGSERIAL`
- `created_at` は `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- `work_log` に `UNIQUE (order_no, process_name)` を含める
- README に定義された `CHECK` 制約を含める
- 以下のインデックスを作成する
  - `idx_work_log_process_end_ts` on `(process_name, end_ts)`
  - `idx_work_log_worker_end_ts` on `(worker_name, end_ts)`
  - `idx_work_log_order_process` on `(order_no, process_name)`

## 型と列定義の扱い

- 列名・型・VARCHAR 長は README の定義に厳密に従う
- `raw_payload_json` は `TEXT` とする
- `ingest_batch_id` は `VARCHAR(30)` とする
- `ingest_batch_id` は秒粒度で採番し、**マイクロ秒は採用しない**（DB設計との整合のため）
- `result_cd`, `source_system`, `process_name` の許容値は README の定義に従う

## 出力に含めてよいもの

- `CREATE TABLE`
- `PRIMARY KEY`
- `UNIQUE`
- `CHECK`
- `CREATE INDEX`
- 可読性のための最小限の SQL コメント

## 出力に含めてはいけないもの

- `DROP TABLE`
- `DROP INDEX`
- `IF EXISTS` を使った防御的削除
- `INSERT` 文やサンプルデータ投入
- `VIEW`, `MATERIALIZED VIEW`
- `FUNCTION`, `PROCEDURE`, `TRIGGER`
- `ENUM` 型の新設
- `import_run` など README にない追加テーブル
- 拡張機能の導入（`CREATE EXTENSION` など）
- パーティション、監査テーブル追加、権限設定などの過剰実装

## 出力形式

- そのまま `psql` で実行できる 1 本の SQL とする
- Markdown の説明文は不要
- SQL コードのみを出力する
- オブジェクト定義の順序は次を推奨する
  1. `work_log`
  2. `work_log_reject`
  3. 制約（必要なら `CREATE TABLE` 内で定義）
  4. インデックス

## 参照ドキュメント

- `results_record_db/README.md`
```

---

### 2.2 SQLAlchemy モデル作成用プロンプト

```
あなたは Python 3.11+ と SQLAlchemy 2 系で PostgreSQL 18.3 に接続するコードを書くエンジニアです。
以下の README を一次情報として扱い、src/db.py を作成してください。

## 要件

- SQLAlchemy を使う
- work_log と work_log_reject をモデル定義する
- DB 接続情報は `db.py` にハードコードする
  - host: `localhost`
  - port: `5432`
  - dbname: `results_record_db`
  - user: `results_user`
  - password: `results_pass`
- セッション管理関数を持つ
- PostgreSQL 18.3 を前提にする
- モデル定義は README のカラム定義、制約、型に従う

## 出力対象

- src/db.py

## 参照ドキュメント

- results_record_db/README.md
- results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md
```

---

### 2.3 共通取込処理作成用プロンプト

```
あなたは Python 3.11+ で CSV / Excel 取込処理を書くエンジニアです。
以下の README を一次情報として扱い、src/ingest.py を作成してください。

## 要件

- 3 種類の元ログを処理対象とする
  - 内装組立ログ
  - 外装組立ログ
  - 出荷検査ログ
- README の採用列 / 捨て列 / 補完ルール / reject 条件に従う
- 内装組立・外装組立の `worker_name` は、READMEのファイル名規則に従って抽出する
- 英字名・日本語名、外装組立の任意ライン識別子、年月6桁または年月日8桁を扱う
- 出荷検査は `inspector_name` を `worker_name` として使用する
- worker_name 正規化ルールに従う
- work_sec の境界条件に従う
- `work_sec` は跨日を許容し、各日ごとの稼働時間帯（08:00〜12:00, 13:00〜17:00）のみを積算する
- duplicate は work_log に入れず、work_log_reject に DUPLICATE_KEY として残す
- `source_row_no` はヘッダを除くデータ行の 1 始まりで記録する
- `raw_payload_json` には元入力行の全列を key-value JSON で保持する（捨て列も含む）
- `ingest_batch_id` は 1ファイル取込ごとに採番する
- SQLAlchemy を使って DB へ登録する
- CLI と Web の両方から呼べるように、入口依存の処理を書かない

## 出力対象

- src/ingest.py

## 参照ドキュメント

- results_record_db/README.md
```

---

### 2.4 CLI 入口作成用プロンプト

```
あなたは Python 3.11+ で CLI ツールを書くエンジニアです。
src/ingest.py を呼び出すための最小 CLI 入口を src/ingest_cli.py として作成してください。

## 要件

- ファイルパスを引数で受け取れる
- source_system / 工程判定は ingest.py 側のファイル名規則に委譲する
- 必要に応じて --order-product-master で補助マスタを受け取れる
- 業務ロジックは書かない
- 実行結果のサマリだけ表示する
```

---

### 2.5 Streamlit 作成用プロンプト

```
あなたは Streamlit で業務向けの簡易 UI を作るエンジニアです。
以下の README を一次情報として扱い、src/streamlit_app.py を作成してください。

## 要件

- PostgreSQL のデータを使って KPI 3 種を表示する
- フィルタは期間・工程・作業者を持つ
- CSV 出力を持つ
- 工程別時間別の作業台数は、工程順を固定表示する
- 工程間滞留は BOP 専用テーブルを作らず、
  内装組立 → 外装組立 → 出荷検査 の固定順で扱う
- 滞留は以下の 2 区間を扱う
  - 内装組立 → 外装組立
  - 外装組立 → 出荷検査
- 工程間滞留は前工程の完了から次工程の開始までとし、次工程で作業中の製番は含めない
- 作業者一覧は work_log の実績データから抽出する
- 画面装飾は最小でよい
- SQLAlchemy 経由で DB に接続する

## 出力対象

- src/streamlit_app.py

## 参照ドキュメント

- results_record_db/README.md
```

---

### 2.6 テスト作成用プロンプト

```
あなたは Python のテストコードを書くエンジニアです。
README の受入条件とテスト期待値を一次情報として、
tests/test_ingest.py, tests/test_duplicate.py, tests/test_kpi.py を作成してください。

## 要件

- 正常取込を確認する
- 必須欠損や日時変換失敗が reject へ入ることを確認する
- duplicate で work_log の件数が増えないことを確認する
- KPI 1〜3 の集計に必要なデータが取得できることを確認する
- 入口ではなく共通取込処理を主対象にする
```

---

## 3. 使い方のコツ

1. **まず README を完成させる** — 一次情報の品質が実装品質を決める
2. **AI には README を一次情報として渡す** — コンテキストを省略しない
3. **1 回で全部書かせない** — DDL / DB / 取込 / UI / テストに分けて依頼する
4. **出力はそのまま使わない** — 必ずレビューしてから採用する
5. **受入条件を基準にする** — 「動くか」ではなく「仕様どおりか」で判断する

---

## 4. このファイルの位置づけ

本ファイルは、README を補助する **実装開始用ガイド** である。

| ドキュメント | 役割 |
|---|---|
| `README.md` | **何を作るか** を定義する（一次情報） |
| 本ファイル | **どう着手するか** を支援する（AI への橋渡し） |

DocDD の観点では、README を一次情報、本ファイルを **AI への橋渡し** として位置づける。
