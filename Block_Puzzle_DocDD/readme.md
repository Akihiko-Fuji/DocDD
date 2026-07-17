# Falling Block Puzzle DocDD Sample

本ディレクトリは、**Document-Driven Development（DocDD）の解説用見本**として、テトリス系落下ブロックゲームを題材に文書体系を整備したサンプルです。

本リポジトリの主目的は、ゲーム実装そのものの巧拙ではなく、**要求・仕様・設計・試験・記録がどのように接続されるかを説明できる状態を保つこと**です。

ここでいう DocDD の価値は「完全な言語非依存」をうたうことではなく、**特定の実装言語へ文書が過度に引きずられないこと**、および **仕様・設計を Python / C# / Java / C++ / Rust / Kotlin など複数言語へ落とし込める契約として記述すること**にあります。

> GitHub に不慣れな方向けメモ:
> - 青字（リンク）をクリックすると、該当ドキュメントへ移動できます。
> - `docs/...` のような記述は「リポジトリ内のファイルパス」です。
> - 迷ったらまず [4.1 最短ルート](#41-最短ルート) から読み進めると、全体像をつかみやすくなります。

---

## 目次

1. [このリポジトリの目的](#1-このリポジトリの目的)
2. [現在の到達点](#2-現在の到達点)
   - 2.1 [完成しているもの](#21-完成しているもの)
   - 2.2 [これから行うもの](#22-これから行うもの)
   - 2.3 [実装ステータス](#23-実装ステータス)
   - 2.4 [コード成果物ディレクトリ方針](#24-コード成果物ディレクトリ方針)
3. [題材の前提](#3-題材の前提)
   - 3.1 [Game Boy 準拠の主な要素](#31-game-boy-準拠の主な要素)
   - 3.2 [本サンプルでの独自整理・拡張](#32-本サンプルでの独自整理拡張)
4. [読む順番](#4-読む順番)
   - 4.1 [最短ルート](#41-最短ルート)
   - 4.2 [文書体系を順に読むルート](#42-文書体系を順に読むルート)
5. [コア 10 文書](#5-コア-10-文書)
   - 5.1 [文書の読み手](#51-文書の読み手)
   - 5.2 [不明瞭な箇所の補完方針](#52-不明瞭な箇所の補完方針)
6. [DocDD として見てほしいポイント](#6-docdd-として見てほしいポイント)
7. [主な参照先](#7-主な参照先)
8. [Disclaimer](#8-disclaimer)

## 1. このリポジトリの目的

本サンプルは、以下を GitHub 上でひと目で把握できるようにすることを目的とします。

- このリポジトリが何の見本なのか
- どの文書から読めば DocDD の流れを理解しやすいか
- Game Boy 準拠部分と独自拡張部分が何か
- コア 10 文書がどこにあるか
- 実装はどの段階か、何が未着手か

補足（初心者向け）:
- 「見本」は、すぐに完成ゲームを動かすためのコード集ではなく、**実装前に文書を整える練習台**という意味です。
- 「DocDD の流れ」は、ざっくり **要求 → 仕様 → 設計 → 試験 → 記録**の順で確認する読み方です。

---

## 2. 現在の到達点

### 2.1 完成しているもの
- DocDD のコア 10 文書を含む文書骨格
- A-TYPE 主軸の要求・外部仕様・内部設計・試験方針
- T-Spin 採用を含む変更記録・決定記録
- 上流から下流へ辿るためのトレーサビリティ文書
- `src/DocDD_coding/` のA-TYPE正本実装
- 盤面、入力、状態遷移、得点、描画を検証する40件の自動テスト

### 2.2 これから行うもの
- テストケースの実行記録蓄積
- B-TYPE 参考仕様の必要に応じた具体化
- replay / config の永続化実装
- 実施記録と将来拡張差分を継続的に蓄積すること

### 2.3 実装ステータス
**A-TYPE最小版は実装済み**です。`src/DocDD_coding/` に正本実装、`tests/DocDD_coding/` と `src/DocDD_coding/test_tspin_lock_integration.py` に自動テストを配置しています。

`docs/` 配下は `00_overview` から `06_records` まで一式が揃っており、内部設計も `27〜39`、品質保証も `40〜46`、プロジェクト管理も `50〜56` が並んでいます。現段階は、**文書から実装・テストまでを追跡できる教材として成立させ、実施記録と将来拡張差分を積み上げる段階**と位置付けます。

補足（初心者向け）:
- コードだけでなく、コードの判断根拠を文書から辿ることが本教材の主眼です。
- 実装を確認するときは、[4.1 最短ルート](#41-最短ルート) または [5. コア 10 文書](#5-コア-10-文書) から根拠文書を確認してください。

### 2.4 コード成果物ディレクトリ方針
- DocDD に基づいて制作するコード成果物は `src/DocDD_coding/` に配置する。
- `src/vibe_coding/vibe_code_tetris.py` は、短いリクエストを入力として生成した**比較用のバイブコーディング成果物**であり、DocDD 正本実装ではない。
- さらに同ファイルは、**DocDD に基づかない実装では SHAPES 定義と文書座標系のズレが生じうる**ことを示す教材として保持する。
- したがって、仕様適合や受入判定の根拠は `docs/` 群および `src/DocDD_coding/` を優先し、`src/vibe_coding/` は比較・検討用途として扱う。

---

## 3. 題材の前提

このサンプルでは、題材としてテトリス系ゲームを用いますが、商用製品の複製を目的としません。

### 3.1 Game Boy 準拠の主な要素
- 十字キー + A/B + SELECT + START の論理入力
- A-TYPE を主軸とする整理
- 10×18 盤面
- NEXT 1 個
- Hold なし
- Hard drop なし
- シンプルな画面構成
- 想定描画解像度 640×576（32×32px の 10×18 盤面を収める固定基準解像度）
- ゲーム中フォントは Early GameBoy を採用候補とし、TTF を実行時に直接読むのではなく 32×32 の PNG グリフへ変換した素材として利用する

### 3.2 本サンプルでの独自整理・拡張
- HID キーボード（標準入力）を主入力としつつ、ゲームパッド対応を前提に論理ボタンへ写像する
- `config.ini` による入力インターフェースとボタン割当の切替を明文化
- T-Spin を独自拡張として採用
- B-TYPE は参考仕様として保持するが初期実装必須から外す
- DocDD の解説に必要なトレーサビリティ、記録、変更波及例を文書化

差分の一覧は [docs/00_overview/04_reference_baseline_and_deltas.md](docs/00_overview/04_reference_baseline_and_deltas.md) を参照してください。

---

## 4. 読む順番

> 初心者向けの使い分け:
> - **まず全体像だけ知りたい** → [4.1 最短ルート](#41-最短ルート)
> - **文書管理の構造まで理解したい** → [4.2 文書体系を順に読むルート](#42-文書体系を順に読むルート)

### 4.1 最短ルート
1. [文書一覧 / Document Map](docs/00_overview/00_document_map.md)  
   文書の全体配置と、各文書の役割を最初に把握するための入口です。
2. [プロジェクト憲章 / Project Charter](docs/00_overview/01_project_charter.md)  
   このサンプルの目的・範囲・前提を確認するための基準文書です。
3. [スコープ定義 / Scope Definition](docs/01_requirements/11_scope_definition.md)  
   「何を対象にし、何を対象外にするか」を明確にします。
4. [追跡マトリクス / Traceability Matrix](docs/01_requirements/16_traceability_matrix.md)  
   要求から設計・試験まで、つながり（追跡性）を確認できます。
5. [モジュール設計 / Module Design](docs/03_internal_design/34_module_design.md)  
   実装を始める前に、内部契約と責務分割を把握するための要点です。
6. [試験戦略 / Test Strategy](docs/04_quality_assurance/40_test_strategy.md)  
   どの観点で品質を保証するかを確認できます。
7. [変更事例（T-Spin 採用）/ Change Case](docs/06_records/64_change_case_tspin_adoption.md)  
   変更がどの文書へ波及するかを具体例で確認できます。

### 4.2 文書体系を順に読むルート
1. [Overview（docs/00_overview）](docs/00_overview)
2. [Requirements（docs/01_requirements）](docs/01_requirements)
3. [External Specification（docs/02_external_spec）](docs/02_external_spec)
4. [Internal Design（docs/03_internal_design）](docs/03_internal_design)
5. [Quality Assurance（docs/04_quality_assurance）](docs/04_quality_assurance)
6. [Records（docs/06_records）](docs/06_records)

補足（初心者向け）:
- フォルダ単位で読むときは、まず各フォルダ内の番号が若い文書（例: `00`, `01`, `11`）から読むと流れを追いやすくなります。

---

## 5. コア 10 文書

本サンプルでは、以下を **DocDD 骨格を支えるコア 10 文書**として扱います。

1. [文書一覧 / Document Map](docs/00_overview/00_document_map.md)  
   全文書の地図。迷ったときの起点です。
2. [プロジェクト憲章 / Project Charter](docs/00_overview/01_project_charter.md)  
   プロジェクトの目的・前提・進め方を定義します。
3. [スコープ定義 / Scope Definition](docs/01_requirements/11_scope_definition.md)  
   対象範囲と非対象を明文化します。
4. [機能要件 / Functional Requirements](docs/01_requirements/13_functional_requirements.md)  
   必要な機能を要求として定義します。
5. [非機能要件 / Non-Functional Requirements](docs/01_requirements/14_non_functional_requirements.md)  
   性能・保守性・運用性など品質面の要求を定義します。
6. [ゲームルール仕様 / Game Rules Spec](docs/02_external_spec/20_game_rules_spec.md)  
   ゲームとしての振る舞いを外部仕様として記述します。
7. [画面仕様 / UI Screen Spec](docs/02_external_spec/21_ui_screen_spec.md)  
   画面構成や表示要素を確認できます。
8. [回転・衝突仕様 / Rotation & Collision Spec](docs/02_external_spec/24_piece_rotation_collision_spec.md)  
   ピース挙動の重要ルールを定義します。
9. [状態機械設計 / State Machine Design](docs/03_internal_design/32_state_machine_design.md)  
   内部状態遷移を設計として明示します。
10. [試験戦略 / Test Strategy](docs/04_quality_assurance/40_test_strategy.md)  
   検証方針とテスト観点の基準を示します。

この 10 文書を起点に、追加文書で詳細化・補助・記録を行います。

補足（初心者向け）:
- 「コア」は **最初に読むべき最小セット**という意味です。
- 全部を一度に読まず、まず [4.1 最短ルート](#41-最短ルート) → 次にこの 10 文書、の順でも問題ありません。

---

## 5.1 文書の読み手

本サンプルの文書は、**人間のレビュー担当者**と**AI による支援・評価系エージェント**の双方が読んで理解できることを意図しています。

そのため、以下を重視します。

- 文書の役割を明確に分ける
- 用語を固定する
- 参照元と独自拡張を分離する
- 曖昧な箇所は未決事項として残すか、主要参照元に基づき補完方針を明記する

### 5.2 不明瞭な箇所の補完方針

Game Boy 版由来の操作感やルールのうち、文書化時点で判断が不足する箇所は、**Game Boy 版テトリスを主要参照元のひとつとして補完**します。

ただし、単に暗黙前提として実装へ押し込むのではなく、補完した場合は以下のいずれかへ反映する方針とします。

- [11_scope_definition.md](docs/01_requirements/11_scope_definition.md)
- [20_game_rules_spec.md](docs/02_external_spec/20_game_rules_spec.md)
- [22_input_operation_spec.md](docs/02_external_spec/22_input_operation_spec.md)
- [24_piece_rotation_collision_spec.md](docs/02_external_spec/24_piece_rotation_collision_spec.md)
- [60_decision_log.md](docs/06_records/60_decision_log.md)

---

## 6. DocDD として見てほしいポイント

- **入口**: README から文書地図へ到達できること
- **役割分離**: 要求・仕様・設計・試験が混ざっていないこと
- **実装接続性**: 文書中の契約記述が Python を含む実装例の一つに閉じず、Python / C# / Java / C++ / Rust / Kotlin へ写像しやすいこと
- **追跡性**: BR → UC → DM → SR/NSR → EXT → Internal Contract → TC を辿れること
- **変更管理**: T-Spin 採用のような変更がどの文書へ波及したか確認できること
- **受入/完了**: プロダクト受入、文書完了、追跡完了を分けて説明していること

補足（初心者向け）:
- 難しく感じたら、「全部を理解する」よりも「どこに何が書いてあるか」を把握することを優先してください。
- 迷子になったら [docs/00_overview/00_document_map.md](docs/00_overview/00_document_map.md) に戻るのが近道です。

---

## 7. 主な参照先

- 文書地図: [docs/00_overview/00_document_map.md](docs/00_overview/00_document_map.md)
- 基準差分: [docs/00_overview/04_reference_baseline_and_deltas.md](docs/00_overview/04_reference_baseline_and_deltas.md)
- スコープ: [docs/01_requirements/11_scope_definition.md](docs/01_requirements/11_scope_definition.md)
- 追跡表: [docs/01_requirements/16_traceability_matrix.md](docs/01_requirements/16_traceability_matrix.md)
- 内部契約: [docs/03_internal_design/34_module_design.md](docs/03_internal_design/34_module_design.md)
- 試験方針: [docs/04_quality_assurance/40_test_strategy.md](docs/04_quality_assurance/40_test_strategy.md)
- 変更見本: [docs/06_records/64_change_case_tspin_adoption.md](docs/06_records/64_change_case_tspin_adoption.md)

## 8. Disclaimer

This project is an educational DocDD sample.
It is not affiliated with, endorsed by, or intended to reproduce any commercial game product.
Bundled runtime assets are project-specific teaching materials; third-party fonts are not bundled.
Product names and trademarks belong to their respective owners.
See [ASSETS.md](ASSETS.md) before adding or reusing visual assets.
