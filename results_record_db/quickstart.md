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

#### Step 1 — PostgreSQL を準備する

- PostgreSQL 18.3 をローカルへ導入する
- ロール `results_user` を作成する
- DB `results_record_db` を作成する

#### Step 2 — DDL を作成・適用する

README の DB 設計を元に DDL を作成し、以下を含める。

- テーブル: `work_log` / `work_log_reject`
- `UNIQUE` 制約
- `CHECK` 制約
- インデックス

#### Step 3 — サンプルデータ取込処理を作る

- 3 種類の元ログを読み込む
- 共通カラムへ正規化する
- 不正データは reject テーブルへ記録する
- duplicate は `DUPLICATE_KEY` として reject に残す

#### Step 4 — 最低限のテストを行う

- 正常取込
- reject
- duplicate
- KPI 集計可能性

#### Step 5 — Streamlit で KPI を表示する

- 期間・工程・作業者でフィルタ
- KPI 3 種を表示
- CSV 出力機能を持つ

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
| Streamlit も同じ DB 層を使う | Streamlit から直接 SQL を書かない |
| 論点を「仕様どおりか」に置く | 「1 発で生成できるか」ではなく仕様適合を重視する |

---

## 2. AI に渡すプロンプト例

> README を一次情報として AI に実装を依頼するためのプロンプト例。  
> そのまま使っても、必要に応じて調整してもよい。

---

### 2.1 DDL 作成用プロンプト

```
あなたは PostgreSQL 18.3 向けの DDL を作成するエンジニアです。
以下の README を一次情報として扱い、DDL を作成してください。

## 要件

- PostgreSQL 方言で記述する
- work_log と work_log_reject の 2 テーブルを作成する
- work_log_id, reject_id は BIGSERIAL
- created_at は TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- UNIQUE (order_no, process_name) を含める
- README に定義された CHECK 制約を含める
- 以下のインデックスを作成する
  - (process_name, end_ts)
  - (worker_name, end_ts)
  - (order_no, process_name)

## 出力形式

- 1 つの SQL ファイルとして、そのまま psql で実行できる形
- コメントを適度に入れる
- DROP は含めない

## 参照ドキュメント

- results_record_db/README.md
```

---

### 2.2 SQLAlchemy モデル作成用プロンプト

```
あなたは Python 3.11 と SQLAlchemy 2 系で PostgreSQL 18.3 に接続するコードを書くエンジニアです。
以下の README を一次情報として扱い、src/db.py を作成してください。

## 要件

- SQLAlchemy を使う
- work_log と work_log_reject をモデル定義する
- 接続 URL は環境変数から受け取れるようにする
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
あなたは Python 3.11 で CSV / Excel 取込処理を書くエンジニアです。
以下の README を一次情報として扱い、src/ingest.py を作成してください。

## 要件

- 3 種類の元ログを処理対象とする
  - 内装組立ログ
  - 外装組立ログ
  - 出荷検査ログ
- README の採用列 / 捨て列 / 補完ルール / reject 条件に従う
- worker_name 正規化ルールに従う
- work_sec の境界条件に従う
- duplicate は work_log に入れず、work_log_reject に DUPLICATE_KEY として残す
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
あなたは Python 3.11 で CLI ツールを書くエンジニアです。
src/ingest.py を呼び出すための最小 CLI 入口を src/ingest_cli.py として作成してください。

## 要件

- ファイルパスと source_system を引数で受け取れる
- 受け取った情報をもとに src/ingest.py を呼ぶ
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
- 作業者一覧は、サンプルデータから抽出した作業者マスターを利用してよい
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
