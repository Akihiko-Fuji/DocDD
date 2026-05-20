# START_HERE

このリポジトリを最初に見る方向けの入口です。

このリポジトリは、  
**「AIを用いたコード開発：仕様の粒度が成果物を決める」**  
というセミナーのために作成した教材リポジトリです。

主題は、AIでコードを速く書くことではありません。

**業務をどう整理し、仕様に落とし、AIや実装に渡せる形にするか**  
を、実例で確認するための教材です。

---

## まず知ってほしいこと

このリポジトリで伝えたいことは、次の3つです。

| 観点 | 内容 | このリポジトリでの対応 |
|---|---|---|
| 何を正とみなすか | データコントラクト | 入力データ、正規化データ、DB制約、reject条件 |
| どこまでできたら完成か | 受入条件 | 正常取込、reject、二重取込、KPI表示の確認 |
| 誰がどう回すか | 運用ガードレール | CLI / Web入口、reject確認、再投入、ログ確認 |

AIにコードを書かせる場合でも、この3つが曖昧なままだと、成果物はぶれます。

逆に、この3つが整理されていれば、AI、外部ベンダー、情シス、現場担当者との会話がしやすくなります。

---

## このリポジトリの全体構成

```text
DocDD/
├── README.md
├── START_HERE.md
│
├── seminars/
│   └── セミナー資料・説明用Markdown
│
├── results_record_db/
│   └── 主教材：製造実績ログをDB化し、KPI可視化する実務例
│
└── Block_Puzzle_DocDD/
    └── 補助教材：DocDDの文書体系を見せるための落下ブロックゲーム例
```

| 場所 | 役割 |
|---|---|
| [`README.md`](./README.md) | リポジトリ全体の説明 |
| [`seminars/`](./seminars/) | セミナー資料・説明用Markdown |
| [`results_record_db/`](./results_record_db/) | 主教材。製造実績ログの正規化・DB取込・KPI可視化 |
| [`Block_Puzzle_DocDD/`](./Block_Puzzle_DocDD/) | 補助教材。DocDDの文書体系と変更波及の例 |

---

## まず読むなら

GitHubやPythonに慣れていない方は、次の順で見るのがおすすめです。

| 順番 | 見るもの | 目的 |
|---:|---|---|
| 1 | [`seminars/01_script.md`](./seminars/01_script.md) | 当日の話の全体像を見る |
| 2 | [`results_record_db/README.md`](./results_record_db/README.md) | 実務題材の設計内容を見る |
| 3 | [`results_record_db/quickstart.md`](./results_record_db/quickstart.md) | 実行手順を見る |
| 4 | [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md) | DocDDの構造教材を見る |
| 5 | [`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md) | 補助教材の文書地図を見る |

まずはすべてを理解しようとせず、  
**どこに何があるか** を把握するだけで十分です。

---

## 10分で見るなら

時間がない場合は、次の3つだけ見てください。

| 順番 | リンク | 見ること |
|---:|---|---|
| 1 | [`seminars/01_script.md`](./seminars/01_script.md) | セミナー全体の主張 |
| 2 | [`results_record_db/README.md`](./results_record_db/README.md) | 製造実績ログを題材にした設計内容 |
| 3 | [`results_record_db/quickstart.md`](./results_record_db/quickstart.md) | 動かす場合の最短手順 |

---

## 30分で見るなら

少し時間がある場合は、次の順がおすすめです。

| 順番 | リンク | 見ること |
|---:|---|---|
| 1 | [`seminars/01_script.md`](./seminars/01_script.md) | セミナー全体の流れ |
| 2 | [`results_record_db/README.md`](./results_record_db/README.md) | 業務モデル、KPI、DB設計、取込方針 |
| 3 | [`results_record_db/quickstart.md`](./results_record_db/quickstart.md) | 実行手順 |
| 4 | [`results_record_db/sample_data/`](./results_record_db/sample_data/) | 正常データ・不正データ・補助マスタ |
| 5 | [`results_record_db/src/ingest.py`](./results_record_db/src/ingest.py) | CSV取込、検証、正規化、reject処理 |
| 6 | [`results_record_db/src/streamlit_app.py`](./results_record_db/src/streamlit_app.py) | Web取込とKPI表示 |
| 7 | [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md) | DocDD補助教材の概要 |
| 8 | [`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md) | 要求・仕様・設計・試験・記録の文書地図 |

---

## 目的別の読み方

### セミナー当日の内容を確認したい

まずはこちらを見てください。

- [`seminars/01_script.md`](./seminars/01_script.md)

セミナーで説明した流れを、Markdown形式で確認できます。

関連ディレクトリ：

- [`seminars/`](./seminars/)

---

### 実務寄りの題材を見たい

こちらが主教材です。

- [`results_record_db/`](./results_record_db/)
- [`results_record_db/README.md`](./results_record_db/README.md)

この教材では、製造現場でよくある次のような状況を扱います。

- 工程ごとにログ形式が違う
- ExcelやCSVの列名・粒度がそろっていない
- そのままではKPI集計に使えない
- 不正データや重複データをどう扱うか決める必要がある
- 最終的にWeb画面でKPIを見たい

主に見るファイルは以下です。

| リンク | 内容 |
|---|---|
| [`results_record_db/README.md`](./results_record_db/README.md) | 設計ガイド |
| [`results_record_db/quickstart.md`](./results_record_db/quickstart.md) | 実行手順 |
| [`results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md) | ローカルPostgreSQL構築手順 |
| [`results_record_db/make_sample_data.md`](./results_record_db/make_sample_data.md) | サンプルデータ設計 |
| [`results_record_db/sample_data/`](./results_record_db/sample_data/) | サンプルCSV |
| [`results_record_db/src/`](./results_record_db/src/) | Python実装 |
| [`results_record_db/tests/`](./results_record_db/tests/) | テスト |

---

### 実際に動かしたい

実行手順はこちらです。

- [`results_record_db/quickstart.md`](./results_record_db/quickstart.md)

ローカルPostgreSQLの準備はこちらです。

- [`results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md)

この教材では、以下の流れを確認できます。

```text
CSVファイル
↓
取込・検証
↓
正常データ / rejectデータの振り分け
↓
PostgreSQLへ登録
↓
StreamlitでKPI可視化
```

実行に関係する主なファイルは以下です。

| リンク | 内容 |
|---|---|
| [`results_record_db/src/db.py`](./results_record_db/src/db.py) | DBモデル、接続、制約 |
| [`results_record_db/src/ingest.py`](./results_record_db/src/ingest.py) | 取込・検証・正規化の共通ロジック |
| [`results_record_db/src/ingest_cli.py`](./results_record_db/src/ingest_cli.py) | CLI入口 |
| [`results_record_db/src/streamlit_app.py`](./results_record_db/src/streamlit_app.py) | Web入口、KPI表示 |
| [`results_record_db/requirements.txt`](./results_record_db/requirements.txt) | 必要ライブラリ |
| [`results_record_db/pytest.ini`](./results_record_db/pytest.ini) | pytest設定 |

---

### DocDDの文書体系を見たい

DocDDの構造を見るための補助教材はこちらです。

- [`Block_Puzzle_DocDD/`](./Block_Puzzle_DocDD/)
- [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md)

この教材は、落下ブロックゲームを題材にしています。

目的はゲームそのものではなく、以下の文書がどうつながるかを見ることです。

```text
要求
↓
仕様
↓
設計
↓
試験
↓
変更記録
```

まずは以下を見るのがおすすめです。

| リンク | 内容 |
|---|---|
| [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md) | 補助教材の概要 |
| [`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md) | 文書一覧・文書地図 |
| [`Block_Puzzle_DocDD/docs/00_overview/01_project_charter.md`](./Block_Puzzle_DocDD/docs/00_overview/01_project_charter.md) | プロジェクト憲章 |
| [`Block_Puzzle_DocDD/docs/01_requirements/11_scope_definition.md`](./Block_Puzzle_DocDD/docs/01_requirements/11_scope_definition.md) | スコープ定義 |
| [`Block_Puzzle_DocDD/docs/01_requirements/16_traceability_matrix.md`](./Block_Puzzle_DocDD/docs/01_requirements/16_traceability_matrix.md) | 追跡マトリクス |
| [`Block_Puzzle_DocDD/docs/03_internal_design/34_module_design.md`](./Block_Puzzle_DocDD/docs/03_internal_design/34_module_design.md) | モジュール設計 |
| [`Block_Puzzle_DocDD/docs/04_quality_assurance/40_test_strategy.md`](./Block_Puzzle_DocDD/docs/04_quality_assurance/40_test_strategy.md) | 試験戦略 |
| [`Block_Puzzle_DocDD/docs/06_records/64_change_case_tspin_adoption.md`](./Block_Puzzle_DocDD/docs/06_records/64_change_case_tspin_adoption.md) | T-Spin採用の変更事例 |

---

## このリポジトリで見てほしいこと

このリポジトリで見てほしいのは、コードの量や派手な画面ではありません。

見てほしいのは、次の流れです。

```text
現場の要求
↓
業務モデル
↓
データ定義
↓
DB設計
↓
取込処理
↓
reject設計
↓
受入条件
↓
KPI可視化
```

AIを使う場合でも、人間側がこの流れを整理しておくことで、成果物がぶれにくくなります。

---

## 主教材：results_record_db

[`results_record_db/`](./results_record_db/) は、製造業の実務に寄せた教材です。

複数工程の作業実績ログを取り込み、共通形式に正規化し、DBに保存し、KPIとして可視化します。

### この教材で扱うこと

| 項目 | 内容 |
|---|---|
| 業務モデル | 1製番 = 1台、内装組立 → 外装組立 → 出荷検査 |
| KPI | 工程別時間別、工程間滞留、作業者別日別実績 |
| 入力データ | 工程ごとに異なるCSVログ |
| 正規化 | 異なるログを `work_log` に揃える |
| reject | 不正行を `work_log_reject` に理由付きで残す |
| DB | PostgreSQL |
| Web画面 | Streamlit |
| テスト | pytest |

### 主なファイル

| リンク | 内容 |
|---|---|
| [`results_record_db/README.md`](./results_record_db/README.md) | 設計ガイド |
| [`results_record_db/quickstart.md`](./results_record_db/quickstart.md) | クイックスタート |
| [`results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md) | ローカルDB構築 |
| [`results_record_db/make_sample_data.md`](./results_record_db/make_sample_data.md) | サンプルデータ設計 |
| [`results_record_db/sample_data/`](./results_record_db/sample_data/) | サンプルデータ |
| [`results_record_db/src/`](./results_record_db/src/) | 実装コード |
| [`results_record_db/tests/`](./results_record_db/tests/) | テストコード |

---

## 補助教材：Block_Puzzle_DocDD

[`Block_Puzzle_DocDD/`](./Block_Puzzle_DocDD/) は、DocDDの文書体系を見せるための教材です。

落下ブロックゲームを題材に、以下のつながりを確認できます。

- 要求
- 仕様
- 設計
- 試験
- 変更記録
- トレーサビリティ

この教材は、ゲーム実装の完成度を競うものではなく、  
**文書を一次情報として開発を進める構造** を見るためのものです。

### 主なファイル

| リンク | 内容 |
|---|---|
| [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md) | 補助教材のREADME |
| [`Block_Puzzle_DocDD/quickstart.md`](./Block_Puzzle_DocDD/quickstart.md) | 実行手順 |
| [`Block_Puzzle_DocDD/docs/`](./Block_Puzzle_DocDD/docs/) | 文書群 |
| [`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md) | 文書地図 |
| [`Block_Puzzle_DocDD/src/`](./Block_Puzzle_DocDD/src/) | 実装コード |
| [`Block_Puzzle_DocDD/tests/`](./Block_Puzzle_DocDD/tests/) | テストコード |

---

## コードを見るときのポイント

`results_record_db/src/` では、主に以下を見てください。

| ファイル | 見るポイント |
|---|---|
| [`results_record_db/src/ingest.py`](./results_record_db/src/ingest.py) | CSV取込、検証、正規化、reject振り分け |
| [`results_record_db/src/ingest_cli.py`](./results_record_db/src/ingest_cli.py) | CLI入口 |
| [`results_record_db/src/streamlit_app.py`](./results_record_db/src/streamlit_app.py) | Web入口、KPI表示 |
| [`results_record_db/src/db.py`](./results_record_db/src/db.py) | DBモデル、制約、接続 |

特に重要なのは、CLIとWebで入口が違っても、  
**取込・検証・正規化のロジックを共通化する** という考え方です。

---

## サンプルデータを見るときのポイント

[`results_record_db/sample_data/`](./results_record_db/sample_data/) には、正常データと不正データの両方があります。

| 種類 | 目的 |
|---|---|
| 正常データ | `work_log` に登録される |
| 不正データ | `work_log_reject` に理由付きで記録される |
| 補助マスタ | 内装組立ログの `product_name` 補完に使う |

この教材では、不正データを単に捨てるのではなく、  
**なぜ取り込まなかったかを残す** ことを重視しています。

---

## このリポジトリが想定している読者

このリポジトリは、特に以下のような方を想定しています。

- 製造業の業務改善に関わる人
- 中小企業診断士
- DX推進担当
- 現場とITの橋渡しをする人
- AIコーディングを業務に使ってみたい人
- 要件定義や仕様書の粒度に悩んでいる人
- 外部ベンダーや情シスに依頼する前に、何を整理すべきか知りたい人

---

## このリポジトリが目的としていないこと

このリポジトリは、以下を目的としていません。

- 高度なプログラミングテクニックを見せること
- 完成された商用システムを提供すること
- AIだけで自動的に業務課題を解決すること
- ゲームそのものの完成度を競うこと

目的は、  
**業務を仕様に翻訳し、AIや実装へ渡せる状態にすること**  
を実例で示すことです。

---

## キーワード

このリポジトリを読む上で重要なキーワードです。

| キーワード | 意味 |
|---|---|
| DocDD | Document-Driven Development。文書駆動開発 |
| データコントラクト | 入力データ・正規化データ・制約の合意 |
| 受入条件 | どこまでできたら完成かを判断する条件 |
| 運用ガードレール | 誰がどう運用し、失敗時にどう戻すかのルール |
| reject | 正常データに入れず、理由付きで除外・保留すること |
| 正規化 | バラバラな入力を、同じ意味・同じ形で扱えるように揃えること |
| KPI | 業務状態を判断するための指標 |

---

## 最後に

AIでコードを書くこと自体は、今後さらに簡単になります。

しかし、業務システムで本当に難しいのは、コードを書く前に、

```text
何を正とするか
どこまでできたら完成か
誰がどう回すか
```

を決めることです。

このリポジトリは、その整理をAI時代にどう行うかを示すための教材です。

**ツールは変わるが、型は残る。**