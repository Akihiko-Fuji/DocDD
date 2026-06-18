# DocDD

このリポジトリは、**中小企業診断士協会 生産革新フォーラム**（MIF研究会）向けセミナー**「AIを用いたコード開発：仕様の粒度が成果物を決める」**  
のために構成した教材・資料リポジトリです。

主目的は、単にコードを作ることではなく、  
**AI を用いた開発においても、仕様の粒度と文書の整理が成果物の質を決める**  
ことを、実例を通して示すことにあります。


## AI時代にDocDDが必要になる理由

ソフトウェア開発の歴史は、機械に近い記述から、人間が理解しやすい記述へと抽象度を高めてきた歴史でもあります。

初期のソフトウェア開発では、機械語やアセンブリ言語など、ハードウェアの動作に近い形式でプログラムを記述する必要がありました。
その後、FORTRANやCOBOLをはじめとする高水準言語とコンパイラが実用化され、人間は機械語の細部を直接扱わずに、より業務や処理内容に近い表現でプログラムを記述できるようになりました。

生成AIの登場によって、この抽象化がさらに一段上へ広がりつつあります。

<img width="1024" height="371" alt="z_名称未設定 1" src="https://github.com/user-attachments/assets/d96b7948-40fb-475f-b907-7538f7b194b4" />


従来、人が主に記述していたものは、Python、Java、C++などの高水準言語でした。
現在は、要求、仕様、制約、受入条件、テスト観点などを自然言語で整理し、AIやCoding Agentの支援を受けながら、高水準言語による実装へ変換することが可能になっています。

ただし、AIはコンパイラと同じものではありません。

高水準言語には厳密な文法と実行規則がありますが、自然言語には曖昧さ、前提の省略、解釈の幅があります。
また、AIが生成するコードは、同じ指示から常に同じ結果が得られる決定的な変換ではありません。

そのため、自然言語で指示できるようになったからといって、仕様を省略できるわけではありません。
むしろ、AIが実装を担う範囲が広がるほど、人間側には次の内容を明確にする役割が求められます。

* 何を実現したいのか
* 何を正しいデータとみなすのか
* どの条件を異常として扱うのか
* どこまでできたら完成なのか
* 誰がどのように運用するのか
* どのようなテストで妥当性を確認するのか
* 変更時に、どの文書や実装へ影響するのか

DocDDでは、これらを要求、仕様、設計、試験、変更記録として整理し、AIと人間が共有する一次情報として扱います。

つまり、AI時代のDocDDは、自然言語をそのまま機械語へ変換するための手法ではありません。
自然言語に含まれる曖昧さを減らし、AIが実装を判断できる粒度まで要求や仕様を整え、その実装結果を検証可能な状態に保つための手法です。

> 高水準言語が、機械語の複雑さを人間から隠したように、生成AIは、実装作業の一部を自然言語の背後へ隠し始めています。
> しかし、隠された実装を正しい方向へ導くためには、仕様の粒度、ドキュメントの質、受入条件、テストがこれまで以上に重要になります。

このリポジトリでは、自然言語の指示だけで一度にコードを生成することを目的としていません。
ドキュメントを一次情報として整理し、実装、テスト、レビュー、変更をつなげることで、AIを用いた開発でも成果物がぶれにくい状態を作ることを目的としています。

※上図は、ソフトウェア開発における抽象化の変化を説明するための概念図です。実際のAI開発では、自然言語から高水準言語への変換だけでなく、コードの実行、テスト、修正、レビューなど複数の工程を含みます。



---

## はじめての方向け（GitHubに不慣れな方へ）

はじめて見る方は、まず [`START_HERE.md`](./START_HERE.md) を参照してください。
以下の順でクリックして読んでいただくと、全体像を把握しやすくなります。

1. セミナー資料の入口：[`seminars/`](./seminars/)
2. 主教材のREADME：[`results_record_db/README.md`](./results_record_db/README.md)
3. 主教材の環境構築：[`results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md)
4. 補助教材のREADME：[`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md)
5. 文書対応マップ：[`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md)

---

## このリポジトリの位置づけ

この[リポジトリ](https://ja.wikipedia.org/wiki/%E3%83%AA%E3%83%9D%E3%82%B8%E3%83%88%E3%83%AA)では、[`seminars/`](./seminars/) 配下のセミナー資料を中心に、  
2つの教材を使って説明を行います。

### 1. [`results_record_db/`](./results_record_db/)
製造業の実務に寄せた題材です。  
複数の設備・工程から出力される異なる形式の実績ログを、共通ルールで正規化し、  
PostgreSQL に取り込み、最終的に Streamlit で KPI を可視化する流れを扱います。

この教材では、特に以下を重視しています。

- 業務モデルの定義
- KPI の定義
- DB 設計
- 取込処理の設計方針
- reject の扱い
- 受入条件の明確化
- AI による実装の一次情報として文書を使うこと

関連ドキュメント：
- [`results_record_db/README.md`](./results_record_db/README.md)
- [`results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md)

### 2. [`Block_Puzzle_DocDD/`](./Block_Puzzle_DocDD/)
DocDD（Document-Driven Development）の構造を見せる教材です。  
有名パズルゲームを元にした題材を使い、

- 要求
- 仕様
- 設計
- 試験
- 変更記録

がどのようにつながるか、  
また、変更時にどこへ波及するかを見通しよく示すためのサンプルです。

こちらは、ゲームそのものを作ることよりも、  
**DocDD の考え方を理解しやすい形で見せること** を目的としています。

関連ドキュメント：
- [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md)
- [`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md)

---

## このリポジトリで主に見てほしいこと

このリポジトリで見てほしいのは、ツール比較そのものではありません。  
中心にあるのは、**「どの粒度で仕様を定義すると、AI によるコード開発でも成果物がぶれにくくなるか」** です。

特に、以下の3点を重視しています。

1. **何を正とみなすか**  
   → データコントラクト

2. **どこまでできたら完成か**  
   → 受入条件

3. **誰がどう回すか**  
   → 運用ガードレール

この3つを先に整理することで、

- AI に渡してもぶれにくい
- ベンダーや情シスと握りやすい
- 検収しやすい
- 現場で運用しやすい

という状態を目指します。

---

## DocDD とは何か

このリポジトリでいう **DocDD（Document-Driven Development）** は、  
文書を増やすこと自体を目的にしたものではありません。

本質は、  
**要件・仕様・設計・試験・変更記録を、実装の前に整理し、相互に追跡できる状態に保つこと**  
にあります。

つまり、文書を「説明資料」としてではなく、  
**開発そのものを制御するための中核成果物**として扱います。

この考え方は、特に以下のような場面で有効です。

- AI によるコード生成を使うとき
- 外注・内製・レビューが混在するとき
- 変更時に影響範囲を追いたいとき
- 実装の前に、曖昧さをできるだけ潰したいとき

---

## 誰向けのリポジトリか

このリポジトリは、特に以下のような人を想定しています。

- 製造業の業務改善やシステム提案に関わる人
- 要件定義書、仕様書、設計書の分け方を整理したい人
- AI と協働しながらも、文書主導を崩したくない人
- 小規模テーマでも、後で壊れにくい設計にしたい人
- DocDD の見本を実例つきで見たい人

---

## まずどこから読むべきか

読む順番としては、以下を推奨します。

1. [`seminars/`](./seminars/)
2. [`results_record_db/README.md`](./results_record_db/README.md)
3. [`results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md)
4. [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md)
5. [`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md)

この順で読むと、

- セミナー全体の狙い
- 実務題材での具体例
- 実装・検証の流れ
- DocDD の構造

を追いやすくなります。

---

## ディレクトリの考え方

### [`seminars/`](./seminars/)
MIF セミナー本体の資料・原稿類

### [`results_record_db/`](./results_record_db/)
実務題材としての製造実績可視化教材

### [`Block_Puzzle_DocDD/`](./Block_Puzzle_DocDD/)
DocDD の構造理解用教材

---

## このリポジトリの価値

このリポジトリの価値は、  
「AI がコードを速く書けること」そのものではありません。

価値の中心は、次の点にあります。

- 仕様の粒度
- 文書同士のつながり
- 実装前に曖昧さを整理すること
- AI に渡す一次情報を整えること
- 変更時に、どこを直すべきか追えること

つまり、このリポジトリは  
**AI 時代でも、文書主導で開発を説明可能な状態に保つための見本**  
として読むのが適切です。

---

## 補足

[`results_record_db/`](./results_record_db/) は、MIF セミナーで実務的な題材として使う主教材です。  
[`Block_Puzzle_DocDD/`](./Block_Puzzle_DocDD/) は、DocDD の構造を理解しやすくするためのおまけ教材です。

どちらも重要ですが、主従関係としては

- **主教材**: [`results_record_db/`](./results_record_db/)
- **補助教材**: [`Block_Puzzle_DocDD/`](./Block_Puzzle_DocDD/)

という位置づけです。

また、今回の開発のレギュレーションとして、『自らがプログラム本体を修正しないこと』を挙げています。
当然ながら自分で修正したほうが早い場面もあるのですが、これは意図的にそうしていません。
ドキュメントを書くことによって修正を実施しています。

また、あくまで『セミナー実演向けに、様々な要素をデフォルメしてデザイン』しているため、業務稼働で必要な要件の一部は考慮していません。
あれが考慮できてない、これが必要だと判断できる場合、それらも要件としてドキュメント化し、DocDD手法で落とし込むことが可能です。

---

## 参照先

- [`seminars/`](./seminars/)
- [`results_record_db/README.md`](./results_record_db/README.md)
- [`results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md`](./results_record_db/results_record_db_LOCAL_POSTGRESQL_SETUP.md)
- [`Block_Puzzle_DocDD/readme.md`](./Block_Puzzle_DocDD/readme.md)
- [`Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`](./Block_Puzzle_DocDD/docs/00_overview/00_document_map.md)
