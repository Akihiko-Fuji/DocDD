# Windows 環境セットアップ手順

このドキュメントは、Windows PC で `results_record_db` を動かすための準備手順です。

対象は、Python や Streamlit にあまり慣れていない方です。

本ドキュメントでは、できるだけ手順を簡単にするため、**Python 仮想環境は作成しません**。  
Windows にインストールした Python 環境へ、必要なライブラリを直接インストールします。

> 補足: Pythonに慣れている方は仮想環境を使っても構いません。  
> ただし、このページでは「まず動かす」ことを優先します。

---

## このページの位置づけ

このページでは、主に以下を扱います。

| 項目 | このページで扱うか |
|---|---|
| Python のインストール | 扱う |
| PowerShell の使い方 | 最小限だけ扱う |
| リポジトリのZIPダウンロード | 扱う |
| Pythonライブラリのインストール | 扱う |
| Streamlit の起動確認 | 扱う |
| PostgreSQL の詳細設定 | 別ページへ誘導 |
| 業務仕様・DB設計の説明 | 別ページへ誘導 |

関連ファイル：

| ファイル | 内容 |
|---|---|
| [`../START_HERE.md`](../START_HERE.md) | リポジトリ全体の入口 |
| [`../README.md`](../README.md) | リポジトリ全体の説明 |
| [`README.md`](./README.md) | `results_record_db` の設計ガイド |
| [`quickstart.md`](./quickstart.md) | 最短実行手順 |
| [`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md) | PostgreSQL セットアップ |
| [`requirements.txt`](./requirements.txt) | 必要なPythonライブラリ一覧 |

---

## 全体の流れ

Windows で動かす場合、流れは次のとおりです。

```text
1. Python をインストールする
2. リポジトリをZIPでダウンロードする
3. PowerShell で results_record_db フォルダへ移動する
4. 必要ライブラリをインストールする
5. PostgreSQL を準備する
6. DDL を適用してテーブルを作成する
7. サンプルデータを取り込む
8. Streamlit を起動する
```

このページでは、主に 1〜4 と 7〜8 を説明します。

PostgreSQL の準備は、  
[`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md)  
を参照してください。

---

## 1. Python をインストールする

Python は公式サイトからダウンロードします。

- [Python 公式ダウンロードページ](https://www.python.org/downloads/windows/)

### インストール時の注意

Windows 版 Python のインストーラでは、最初の画面で必ず以下にチェックを入れてください。

```text
Add python.exe to PATH
```

これを忘れると、PowerShell で `python` や `py` コマンドが使えない場合があります。

### 推奨

特別な理由がなければ、公式サイトの最新版を利用してください。

Microsoft Store 版 Python でも動く場合がありますが、環境差で混乱しやすいため、セミナー教材では公式サイト版を推奨します。

---

## 2. PowerShell を開く

Windows のスタートメニューで、以下を検索して開きます。

```text
PowerShell
```

以降のコマンドは、基本的に PowerShell で実行します。

---

## 3. Python が使えるか確認する

PowerShell で以下を実行します。

```powershell
py --version
```

または、

```powershell
python --version
```

どちらかで Python のバージョンが表示されればOKです。

例：

```text
Python 3.12.x
```

pip も確認します。

```powershell
py -m pip --version
```

または、

```powershell
python -m pip --version
```

---

## 4. リポジトリをZIPでダウンロードする

Gitに慣れていない場合は、ZIPでダウンロードするのが簡単です。

1. [`DocDD` リポジトリ](https://github.com/Akihiko-Fuji/DocDD) を開く
2. 緑色の `Code` ボタンを押す
3. `Download ZIP` を選ぶ
4. ZIPファイルをダウンロードする
5. ZIPファイルを右クリックして展開する

展開すると、通常は次のようなフォルダ名になります。

```text
DocDD-main
```

---

## 5. results_record_db フォルダへ移動する

PowerShell で、展開したフォルダ内の `results_record_db` へ移動します。

例：ダウンロードフォルダに展開した場合

```powershell
cd $HOME\Downloads\DocDD-main\results_record_db
```

デスクトップに展開した場合は、たとえば以下のようになります。

```powershell
cd $HOME\Desktop\DocDD-main\results_record_db
```

現在の場所を確認したい場合は、以下を実行します。

```powershell
pwd
```

フォルダ内のファイル一覧を確認する場合は、以下を実行します。

```powershell
dir
```

`README.md` や `quickstart.md` が見えていれば、`results_record_db` フォルダに入れています。

---

## 6. pip を更新する

Pythonライブラリをインストールする前に、pipを更新します。

```powershell
py -m pip install --upgrade pip
```

うまくいかない場合は、以下も試してください。

```powershell
python -m pip install --upgrade pip
```

---

## 7. 必要ライブラリをインストールする

`requirements.txt` から必要なライブラリをインストールします。

```powershell
py -m pip install -r requirements.txt
```

うまくいかない場合は、以下も試してください。

```powershell
python -m pip install -r requirements.txt
```

関連ファイル：

- [`requirements.txt`](./requirements.txt)

---

## 8. requirements.txt でうまくいかない場合

`requirements.txt` でインストールできない場合は、必要なライブラリを個別に入れます。

```powershell
py -m pip install pandas sqlalchemy "psycopg[binary]" streamlit pytest openpyxl
```

または、

```powershell
python -m pip install pandas sqlalchemy "psycopg[binary]" streamlit pytest openpyxl
```

---

## 9. インストール確認

以下を実行します。

```powershell
python -c "import pandas, sqlalchemy, streamlit; print('OK')"
```

次のように表示されれば、主要ライブラリは読み込めています。

```text
OK
```

pytest も確認します。

```powershell
pytest --version
```

または、

```powershell
python -m pytest --version
```

---

## 10. PostgreSQL を準備する

この教材では、PostgreSQL を使います。

PostgreSQL の準備は、以下を参照してください。

- [`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md)

PostgreSQL の公式ダウンロードページはこちらです。

- [PostgreSQL Windows Downloads](https://www.postgresql.org/download/windows/)
- [EDB PostgreSQL インストーラ](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)

この教材で使う主な設定は以下です。

| 項目 | 値 |
|---|---|
| DB名 | `results_record_db` |
| ユーザー | `results_user` |
| パスワード | `results_pass` |
| ホスト | `localhost` |
| ポート | `5432` |

接続URLの例：

```text
postgresql+psycopg://results_user:results_pass@localhost:5432/results_record_db
```

---

## 11. DDL を適用する

PostgreSQL の準備ができたら、テーブルを作成します。

DDLファイル：

- [`ddl/ddl_results_record_db.sql`](./ddl/ddl_results_record_db.sql)

PowerShell で `results_record_db` フォルダにいる状態なら、以下のように実行します。

```powershell
psql -U results_user -h localhost -d results_record_db -f ddl\ddl_results_record_db.sql
```

`psql` が見つからない場合は、PostgreSQL の `bin` フォルダに PATH が通っていない可能性があります。

例：

```text
C:\Program Files\PostgreSQL\18\bin
```

PATH設定の詳細は、  
[`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md)  
を参照してください。

---

## 12. テストを実行する

PythonライブラリとDBの準備ができたら、テストを実行します。

```powershell
python -m pytest -q
```

関連ファイル：

| ファイル | 内容 |
|---|---|
| [`tests/`](./tests/) | テストコード |
| [`pytest.ini`](./pytest.ini) | pytest設定 |

---

## 13. サンプルデータをCLIで取り込む

標準サンプルデータは、以下にあります。

- [`sample_data/`](./sample_data/)

まずは内装組立ログを取り込みます。

```powershell
python src\ingest_cli.py sample_data\INTASM_HanaYamada_202601.csv --order-product-master sample_data\order_product_master.csv
```

標準データを順番に取り込む場合は、以下を実行します。

```powershell
python src\ingest_cli.py sample_data\INTASM_HanaYamada_202601.csv --order-product-master sample_data\order_product_master.csv
python src\ingest_cli.py sample_data\INTASM_KentoTakahashi_202601.csv --order-product-master sample_data\order_product_master.csv

python src\ingest_cli.py sample_data\EXTASM_MunekiYoshimura_202601.csv
python src\ingest_cli.py sample_data\EXTASM_ToshioAndo_202601.csv
python src\ingest_cli.py sample_data\EXTASM_ShuheiYamashita_202601.csv

python src\ingest_cli.py sample_data\SHIPCHK_202601.csv
```

関連ファイル：

| ファイル | 内容 |
|---|---|
| [`src/ingest_cli.py`](./src/ingest_cli.py) | CLI入口 |
| [`src/ingest.py`](./src/ingest.py) | 取込・検証・正規化 |
| [`sample_data/order_product_master.csv`](./sample_data/order_product_master.csv) | 補助マスタ |
| [`sample_data/`](./sample_data/) | サンプルCSV |

---

## 14. 不正データの動きを確認する

不正データも `sample_data` に用意しています。

例：

```powershell
python src\ingest_cli.py sample_data\INTASM_HanaYamadaInvalid_202601.csv --order-product-master sample_data\order_product_master.csv
python src\ingest_cli.py sample_data\EXTASM_MunekiYoshimuraInvalid_202601.csv
python src\ingest_cli.py sample_data\SHIPCHK_202601_invalid.csv
```

不正データは、正常テーブル `work_log` ではなく、rejectテーブル `work_log_reject` に理由付きで記録されます。

関連説明：

- [`quickstart.md`](./quickstart.md)
- [`README.md`](./README.md)

---

## 15. Streamlit を起動する

サンプルデータを取り込んだら、Streamlitを起動します。

```powershell
streamlit run src\streamlit_app.py
```

または、

```powershell
python -m streamlit run src\streamlit_app.py
```

ブラウザが自動で開く場合があります。

開かない場合は、PowerShell に表示されるURLをブラウザで開きます。

例：

```text
http://localhost:8501
```

関連ファイル：

- [`src/streamlit_app.py`](./src/streamlit_app.py)

---

## 16. Streamlit で確認すること

Streamlit画面では、以下を確認します。

| 画面・機能 | 確認内容 |
|---|---|
| Import | CSVをアップロードし、検証・プレビュー・登録できる |
| KPI1 | 工程別・時間別の作業台数が見える |
| KPI2 | 工程間滞留が見える |
| KPI3 | 作業者ごとの日別作業台数が見える |
| CSV出力 | 集計結果をCSVで出力できる |

詳細は以下も参照してください。

- [`quickstart.md`](./quickstart.md)
- [`README.md`](./README.md)

---

## 17. よくあるエラー

### `python` が見つからない

エラー例：

```text
python は、内部コマンドまたは外部コマンド...
```

対処：

```powershell
py --version
```

を試してください。

それでも駄目な場合は、Pythonを再インストールし、インストール時に以下へチェックを入れてください。

```text
Add python.exe to PATH
```

---

### `pip` が見つからない

対処：

```powershell
py -m pip --version
```

または、

```powershell
python -m pip --version
```

`pip` 単体で実行するより、`python -m pip` または `py -m pip` の形が安定します。

---

### `psql` が見つからない

エラー例：

```text
psql : 用語 'psql' は認識されません...
```

PostgreSQL の `bin` フォルダに PATH が通っていない可能性があります。

例：

```text
C:\Program Files\PostgreSQL\18\bin
```

詳細は以下を参照してください。

- [`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md)

---

### DB接続エラーになる

エラー例：

```text
connection failed
password authentication failed
database "results_record_db" does not exist
```

確認すること：

| 確認項目 | 期待値 |
|---|---|
| DB名 | `results_record_db` |
| ユーザー | `results_user` |
| パスワード | `results_pass` |
| PostgreSQL起動 | 起動している |
| DDL適用 | 済んでいる |

関連ファイル：

- [`src/db.py`](./src/db.py)
- [`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md)

---

### `ModuleNotFoundError` が出る

エラー例：

```text
ModuleNotFoundError: No module named 'pandas'
```

ライブラリが未インストールです。

対処：

```powershell
py -m pip install -r requirements.txt
```

または、

```powershell
python -m pip install -r requirements.txt
```

---

### Streamlit の画面は出るがデータがない

サンプルデータをまだDBに取り込んでいない可能性があります。

先にCLIでサンプルデータを取り込んでください。

```powershell
python src\ingest_cli.py sample_data\INTASM_HanaYamada_202601.csv --order-product-master sample_data\order_product_master.csv
```

または、Streamlit の Import 画面からCSVをアップロードしてください。

---

### `streamlit` が見つからない

エラー例：

```text
streamlit : 用語 'streamlit' は認識されません...
```

この場合は、以下で起動してください。

```powershell
python -m streamlit run src\streamlit_app.py
```

それでも駄目な場合は、Streamlitをインストールします。

```powershell
py -m pip install streamlit
```

---

## 18. Windowsで使う主なコマンドまとめ

`results_record_db` フォルダで実行する主なコマンドです。

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

python -m pytest -q

python src\ingest_cli.py sample_data\INTASM_HanaYamada_202601.csv --order-product-master sample_data\order_product_master.csv

python -m streamlit run src\streamlit_app.py
```

---

## 19. Gitを使う場合

Gitに慣れている方は、ZIPではなくGitで取得しても構いません。

Git for Windows：

- [Git for Windows](https://git-scm.com/downloads/win)

取得例：

```powershell
git clone https://github.com/Akihiko-Fuji/DocDD.git
cd DocDD\results_record_db
```

Gitを使うと、更新差分を取り込みやすくなります。

ただし、初めての方はZIPダウンロードで問題ありません。

---

## 20. 補足：仮想環境を使う場合

このページでは、簡単に動かすために仮想環境を使わない手順を説明しました。

Pythonに慣れている方や、PC全体のPython環境を汚したくない場合は、仮想環境を使う方法もあります。

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PowerShellで実行ポリシーのエラーが出る場合は、以下を実行します。

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.venv\Scripts\activate
```

ただし、初めてPythonを触る方には少し難しいため、まずは通常環境での実行を優先して構いません。

---

## 21. 関連リンク

### リポジトリ内リンク

| リンク | 内容 |
|---|---|
| [`../START_HERE.md`](../START_HERE.md) | 最初に読む入口 |
| [`../README.md`](../README.md) | リポジトリ全体の説明 |
| [`README.md`](./README.md) | `results_record_db` 設計ガイド |
| [`quickstart.md`](./quickstart.md) | クイックスタート |
| [`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md) | PostgreSQLセットアップ |
| [`requirements.txt`](./requirements.txt) | Python依存ライブラリ |
| [`sample_data/`](./sample_data/) | サンプルデータ |
| [`src/`](./src/) | 実装コード |
| [`tests/`](./tests/) | テストコード |

### 外部リンク

| リンク | 内容 |
|---|---|
| [Python 公式ダウンロードページ](https://www.python.org/downloads/windows/) | Windows版Python |
| [Git for Windows](https://git-scm.com/downloads/win) | Gitを使う場合 |
| [PostgreSQL Windows Downloads](https://www.postgresql.org/download/windows/) | PostgreSQL公式 |
| [EDB PostgreSQL インストーラ](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) | Windows向けPostgreSQLインストーラ |
| [Streamlit Installation](https://docs.streamlit.io/get-started/installation) | Streamlit公式インストール手順 |

---

## 22. 補足

このページは、Windows環境で最初に詰まりやすい部分を補足するためのものです。

実務システムとしての設計内容は、以下を参照してください。

- [`README.md`](./README.md)

実行の最短手順は、以下を参照してください。

- [`quickstart.md`](./quickstart.md)

PostgreSQLの詳細な準備は、以下を参照してください。

- [`results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db_LOCAL_POSTGRESQL_SETUP.md)

---

## 補足：現行配布版での依存導入

本文中の個別パッケージ導入例は解説用に残すが、実際のセットアップでは
`altair` を含む `requirements.txt` を使用する。

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

`py` が利用できない場合は、`py` を `python` に置き換える。
