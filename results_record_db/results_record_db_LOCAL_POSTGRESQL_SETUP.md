# ローカル PostgreSQL セットアップと DDL 適用手順

## 目的

本ドキュメントは、`results_record_db` テーマの実装・検証用に、ローカル環境へ PostgreSQL を導入し、ロールとデータベースを作成し、AI で作成した DDL を適用するまでの最小手順を整理するためのものです。

本テーマでは、**PostgreSQL をローカルで動かし、Python から接続して取り込み・可視化まで行う** ことを前提とします。

---

## このドキュメントで固定すること

- DB 製品: PostgreSQL
- 想定バージョン: PostgreSQL 18
- 接続先: ローカルホスト
- DB 名: `results_record_db`
- ロール名: `results_user`
- スキーマ: `public` を利用
- 文字コード: UTF-8

> 補足: 本テーマではローカル検証を優先し、スキーマ分割や本格的な権限制御は最小限にとどめます。

---

## 1. PostgreSQL の導入

PostgreSQL をローカル PC に導入します。Windows版は

https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

からダウンロード可能です。今回は18.3を導入します。

### Windows の場合
- 公式インストーラを利用して PostgreSQL をインストールする
- インストール時に `postgres` 管理者パスワードを設定する
- `psql` コマンドが利用できるように  に PATH を通す、付属の SQL Shell を使う
- インストール先を変更していない場合、PATH はシステム → システムの詳細設定 → PATHに `C:\Program Files\PostgreSQL\18\bin` を追加
- スタックビルダは `psqlODBC x64` のみ導入

### Linux の場合（例: Debian / Ubuntu）
```bash
sudo apt update
sudo apt install postgresql postgresql-client
```

### 動作確認
```bash
psql --version
```

---

## 2. 管理者ユーザーで接続

まずは管理者権限で PostgreSQL に接続します。

### Windows
SQL Shell (`psql`) またはターミナルから接続

```bash
psql -U postgres -h localhost
```

### Linux
```bash
sudo -u postgres psql
```

---

## 3. ロールを作成する

今回のテーマ専用に、一般利用ロール `results_user` を作成します。

```sql
CREATE ROLE results_user
LOGIN
PASSWORD 'results_pass'
NOSUPERUSER
NOCREATEDB
NOCREATEROLE
INHERIT;
```

> パスワードはローカル検証用の仮設定です。実運用に使う場合は必ず変更してください。

---

## 4. データベースを作成する

```sql
CREATE DATABASE results_record_db
OWNER results_user
ENCODING 'UTF8';
```

作成後、接続先を切り替えます。

```sql
\c results_record_db
```

---

## 5. 権限を確認する

通常はオーナーが `results_user` なのでそのまま使えますが、念のため確認します。

```sql
GRANT ALL PRIVILEGES ON DATABASE results_record_db TO results_user;
```

---

## 6. Python から接続するための接続情報

ローカル検証時の接続 URL 例です。

```text
postgresql+psycopg://results_user:results_pass@localhost:5432/results_record_db
```

従来の `psycopg2` を使う場合は以下でも可です。

```text
postgresql+psycopg2://results_user:results_pass@localhost:5432/results_record_db
```

---

## 7. DDL を作成する際の前提条件

AI に DDL を作成させる際は、以下を固定条件として与えます。

### 対象テーブル
- `work_log`
- `work_log_reject`

### 必須要件
- PostgreSQL 方言で書く
- `work_log_id`, `reject_id` は `BIGSERIAL`
- `created_at` は `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- `UNIQUE (order_no, process_name)` を持つ
- README に定義した `CHECK` 制約を含める
- `process_name + end_ts`
- `worker_name + end_ts`
- `order_no + process_name`
  のインデックスを作成する

### 期待する出力
- `CREATE TABLE work_log`
- `CREATE TABLE work_log_reject`
- `ALTER TABLE ... ADD CONSTRAINT ...`
- `CREATE INDEX ...`

> 補足: セミナー題材としては、1ファイルにまとめても、`01_tables.sql` / `02_indexes.sql` のように分けてもよいです。

---

## 8. DDL 適用手順

AI で作成した DDL を、たとえば `ddl_results_record_db.sql` として保存した場合、以下で適用します。

```bash
psql -U results_user -h localhost -d results_record_db -f ddl_results_record_db.sql
```

Linux で `postgres` ユーザー経由で行う場合:

```bash
psql -U results_user -d results_record_db -f ddl_results_record_db.sql
```

---

## 9. 適用後の確認

### テーブル確認
```sql
\dt
```

### カラム確認
```sql
\d work_log
\d work_log_reject
```

### インデックス確認
```sql
\di
```

### 想定どおりの制約があるか確認
- `UNIQUE (order_no, process_name)`
- `CHECK (end_ts >= start_ts)`
- `CHECK (elapsed_sec >= 0)`
- `CHECK (work_sec >= 0 AND work_sec <= elapsed_sec)`

---

## 10. Python 側で必要なパッケージ

```bash
pip install sqlalchemy psycopg pandas streamlit
```

> 補足: `pandas` や `streamlit` は実装上使うが、本ドキュメントでは詳細説明を目的としない。

---

## 11. セミナー用の運用方針

今回のセミナーでは、以下の方針で進める。

- DDL は AI で作成する様子を見せる
- ただし実行は事前検証済み版を使う
- 論点は「生成できるか」ではなく「仕様どおりか」
- PostgreSQL はローカル環境で動かし、その場で接続確認とテーブル確認を行う

---

## 12. 今後 README に追記するとよい補足

本テーマの README だけでは不足しやすいので、以下は別途明示すると実装が安定する。

- PostgreSQL の想定バージョン
- Python の想定バージョン
- 利用ドライバ（`psycopg` / `psycopg2`）
- DDL 出力ファイル名のルール
- 接続 URL の例
- ローカル検証用のロール名 / DB 名

---

## 付録: そのまま実行できる最小 SQL

```sql
CREATE ROLE results_user
LOGIN
PASSWORD 'results_pass'
NOSUPERUSER
NOCREATEDB
NOCREATEROLE
INHERIT;

CREATE DATABASE results_record_db
OWNER results_user
ENCODING 'UTF8';
```
