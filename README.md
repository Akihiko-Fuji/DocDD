# DocDD

**Document-Driven Development（DocDD）** の考え方を、
実際に読めるドキュメント群として示すための見本リポジトリです。

このリポジトリの主目的は、コードを先に書くことではありません。
**要件定義 → 仕様 → 設計 → テスト** を文書として分離し、
さらにそれらを**相互に追跡できる状態で維持すること**を主題にしています。

---

## このリポジトリが扱うもの

現在の主題は、`Block_Puzzle_DocDD/` 配下にある
**Falling Block Puzzle DocDD Sample（落下ブロックゲームを題材にした DocDD サンプル）**です。

- 題材: Game Boy 版テトリスを参照元のひとつとした落下ブロックゲーム
- 主軸: **A-TYPE**
- 参考扱い: **B-TYPE**
- 目的: ゲーム実装そのものよりも、**DocDD に適した文書体系を成立させること**

このサンプルは、既存商用作品の完全再現を目的とするものではありません。
**公開可能な題材を使って、実務に近い文書構造と変更管理の考え方を示すこと**を目的としています。

---

## このリポジトリで見せたいこと

このリポジトリでは、次のような状態を意図的に作っています。

- 要件定義書が「何を満たすべきか」を定義している
- 仕様書が「外から見てどう振る舞うか」を定義している
- 設計書が「内部でどう作るか」を定義している
- テスト方針書が「何をどう検証するか」を定義している
- 変更時に、**どの文書を直すべきか**が追跡できる
- 実装変更と文書変更が分離せず、**不整合を起こしにくい**

つまり、ドキュメントを「書いて終わりの説明資料」ではなく、
**開発そのものを制御するための中核成果物**として扱っています。

---

## このサンプルの特徴

`Block_Puzzle_DocDD/` の Falling Block Puzzle DocDD Sample では、特に以下を重視しています。

- **要件・仕様・設計・テストの役割分離**
- **コア文書を先に固める構成**
- **トレーサビリティを意識した文書IDと文書間参照**
- **変更時に文書改定を必須とする運用**
- **小規模題材でも曖昧にしない実務寄りの粒度**
- **人間と AI の双方が読んで理解・評価しやすい文書構成**

また、`Block_Puzzle_DocDD/AGENT.md` では、このリポジトリにおける基本ルールとして
**“No behavior change without document change.”**
を明示しています。

これはつまり、

> 機能追加・機能改修・仕様変更を行うときは、
> 必ず対応するドキュメント改定とセットで扱う

という方針です。

---

## 誰向けのリポジトリか

このリポジトリは、特に次のような人を想定しています。

- 要件定義書・仕様書・設計書の分け方を学びたい人
- ドキュメント駆動開発の見本が欲しい人
- 小規模開発でも文書体系を崩したくない人
- 変更時の影響範囲を追える開発をしたい人
- AI と協働しながらも、文書を主導権として保ちたい人

逆に、このリポジトリは
**「最短でゲームを完成させること」だけを目的にしたサンプルではありません。**

---

## まずどこから読むべきか

読む順番としては、まず以下を推奨します。

1. `Block_Puzzle_DocDD/readme.md`
2. `Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`
3. `Block_Puzzle_DocDD/docs/00_overview/01_project_charter.md`
4. `Block_Puzzle_DocDD/docs/01_requirements/11_scope_definition.md`
5. `Block_Puzzle_DocDD/docs/01_requirements/13_functional_requirements.md`
6. `Block_Puzzle_DocDD/docs/01_requirements/14_non_functional_requirements.md`
7. `Block_Puzzle_DocDD/docs/02_external_spec/20_game_rules_spec.md`
8. `Block_Puzzle_DocDD/docs/02_external_spec/21_ui_screen_spec.md`
9. `Block_Puzzle_DocDD/docs/02_external_spec/24_piece_rotation_collision_spec.md`
10. `Block_Puzzle_DocDD/docs/03_internal_design/32_state_machine_design.md`
11. `Block_Puzzle_DocDD/docs/04_quality_assurance/40_test_strategy.md`

この順序で読むと、

**なぜ作るのか → 何を作るのか → どう振る舞うのか → 内部でどう整理するのか → どう検証するのか**

という流れが追いやすくなります。

---

## `Block_Puzzle_DocDD/` サンプルに含まれる中核文書

現在の `Block_Puzzle_DocDD/` Falling Block Puzzle DocDD Sample では、以下をコア文書として位置付けています。

- `00_document_map.md`
- `01_project_charter.md`
- `11_scope_definition.md`
- `13_functional_requirements.md`
- `14_non_functional_requirements.md`
- `20_game_rules_spec.md`
- `21_ui_screen_spec.md`
- `24_piece_rotation_collision_spec.md`
- `32_state_machine_design.md`
- `40_test_strategy.md`

これらは、DocDD の骨格を成立させるための最小セットです。

---

## このリポジトリの見方

このリポジトリを見るときは、単に文書の有無だけではなく、
以下の観点で見てもらえると面白いと思います。

### 1. 文書の役割が分かれているか
- 要件と仕様が混ざっていないか
- 仕様と設計が混ざっていないか
- テストが仕様から導かれているか

### 2. 変更に追従できるか
- ルールを変えたらどの文書を直すべきか
- 状態遷移を変えたらどこへ波及するか
- テストケースは何を根拠に存在するのか

### 3. 実装の前に整理ができているか
- 曖昧なままコードに押し込まずに済んでいるか
- 「なぜこの実装が必要か」を文書から説明できるか
- 人間レビューと AI 補助の両方に耐える形で記述されているか

---

## ディレクトリの考え方

このリポジトリでは、文書を大きく以下のように分けています。

- `00_overview`
  入口、目的、前提、文書構成

- `01_requirements`
  スコープ、機能要求、非機能要求

- `02_external_spec`
  外から見たルール、画面、操作、挙動

- `03_internal_design`
  状態遷移、内部構造、設計上の責務分担

- `04_quality_assurance`
  テスト方針、試験観点、品質確認

- `05_project_management`
  開発ルール、変更管理、進め方

- `06_records`
  判断履歴、変更履歴、レビュー記録

---

## 現在の位置付け

このリポジトリは、完成済み製品の公開というよりも、
**DocDD を学ぶための構造化された見本**です。

そのため、価値の中心は次の点にあります。

- 文書の粒度
- 文書同士のつながり
- 変更時の考え方
- 実装より前に思考を整理するプロセス
- AI を使っても文書主導を崩さないためのルール設計

現時点の `Block_Puzzle_DocDD/` は、**実装完了済みのゲーム配布物ではなく、文書体系を先に成立させる段階**として読むのが適切です。

---

## 補足

`Block_Puzzle_DocDD/` はあくまで題材です。
本当に見てほしいのは、ゲームそのもの以上に、
**「どのように文書体系を作ると、開発を説明可能な状態に保てるか」** という点です。

もしこのリポジトリが役立つとすれば、それは
「きれいな仕様書があるから」ではなく、
**仕様・設計・テスト・変更理由が一連でつながっているから**です。

また、文書中に判断が不足している箇所や、指示が曖昧な箇所がある場合は、
**Game Boy 版テトリスを主要参照元のひとつとして補完しつつ、補完内容がどこに反映されるべきかを文書上で明確にする** 方針を採ります。

---

## 参照先

詳細は以下を参照してください。

- `Block_Puzzle_DocDD/readme.md`
- `Block_Puzzle_DocDD/docs/00_overview/00_document_map.md`
- `Block_Puzzle_DocDD/docs/00_overview/04_reference_baseline_and_deltas.md`
