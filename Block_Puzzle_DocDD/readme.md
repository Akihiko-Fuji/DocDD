# Falling Block Puzzle DocDD Sample

本ディレクトリは、**Document-Driven Development（DocDD）の解説用見本**として、テトリス系落下ブロックゲームを題材に文書体系を整備したサンプルです。

本リポジトリの主目的は、ゲーム実装そのものの巧拙ではなく、**要求・仕様・設計・試験・記録がどのように接続されるかを説明できる状態を保つこと**です。

---

## 1. このリポジトリの目的

本サンプルは、以下を GitHub 上でひと目で把握できるようにすることを目的とします。

- このリポジトリが何の見本なのか
- どの文書から読めば DocDD の流れを理解しやすいか
- Game Boy 準拠部分と独自拡張部分が何か
- コア 10 文書がどこにあるか
- 実装はどの段階か、何が未着手か

---

## 2. 現在の到達点

### 2.1 完成しているもの
- DocDD のコア 10 文書を含む文書骨格
- A-TYPE 主軸の要求・外部仕様・内部設計・試験方針
- T-Spin 採用を含む変更記録・決定記録
- 上流から下流へ辿るためのトレーサビリティ文書

### 2.2 これから行うもの
- 実装基盤の最終確定
- 文書に従った実装着手
- テストケースの実行記録蓄積
- B-TYPE 参考仕様の必要に応じた具体化

### 2.3 実装ステータス
**実装は未着手、または本格着手前の文書整備フェーズ**です。現時点では、コード完成物を示すリポジトリではなく、DocDD の見本として文書体系を先に成立させる段階にあります。

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

### 3.2 本サンプルでの独自整理・拡張
- PC 向けキーボード写像を明文化
- T-Spin を独自拡張として採用
- B-TYPE は参考仕様として保持するが初期実装必須から外す
- DocDD の解説に必要なトレーサビリティ、記録、変更波及例を文書化

差分の一覧は `docs/00_overview/04_reference_baseline_and_deltas.md` を参照してください。

---

## 4. 読む順番

### 4.1 最短ルート
1. `docs/00_overview/00_document_map.md`
2. `docs/00_overview/01_project_charter.md`
3. `docs/01_requirements/11_scope_definition.md`
4. `docs/01_requirements/16_traceability_matrix.md`
5. `docs/03_internal_design/34_module_design.md`
6. `docs/04_quality_assurance/40_test_strategy.md`
7. `docs/06_records/64_change_case_tspin_adoption.md`

### 4.2 文書体系を順に読むルート
1. Overview
2. Requirements
3. External Specification
4. Internal Design
5. Quality Assurance
6. Records

---

## 5. コア 10 文書

本サンプルでは、以下を **DocDD 骨格を支えるコア 10 文書**として扱います。

1. `docs/00_overview/00_document_map.md`
2. `docs/00_overview/01_project_charter.md`
3. `docs/01_requirements/11_scope_definition.md`
4. `docs/01_requirements/13_functional_requirements.md`
5. `docs/01_requirements/14_non_functional_requirements.md`
6. `docs/02_external_spec/20_game_rules_spec.md`
7. `docs/02_external_spec/21_ui_screen_spec.md`
8. `docs/02_external_spec/24_piece_rotation_collision_spec.md`
9. `docs/03_internal_design/32_state_machine_design.md`
10. `docs/04_quality_assurance/40_test_strategy.md`

この 10 文書を起点に、追加文書で詳細化・補助・記録を行います。

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

- `11_scope_definition.md`
- `20_game_rules_spec.md`
- `22_input_operation_spec.md`
- `24_piece_rotation_collision_spec.md`
- `60_decision_log.md`

---

## 6. DocDD として見てほしいポイント

- **入口**: README から文書地図へ到達できること
- **役割分離**: 要求・仕様・設計・試験が混ざっていないこと
- **追跡性**: BR → UC → DM → SR/NSR → EXT → Internal Contract → TC を辿れること
- **変更管理**: T-Spin 採用のような変更がどの文書へ波及したか確認できること
- **受入/完了**: プロダクト受入、文書完了、追跡完了を分けて説明していること

---

## 7. 主な参照先

- 文書地図: `docs/00_overview/00_document_map.md`
- 基準差分: `docs/00_overview/04_reference_baseline_and_deltas.md`
- スコープ: `docs/01_requirements/11_scope_definition.md`
- 追跡表: `docs/01_requirements/16_traceability_matrix.md`
- 内部契約: `docs/03_internal_design/34_module_design.md`
- 試験方針: `docs/04_quality_assurance/40_test_strategy.md`
- 変更見本: `docs/06_records/64_change_case_tspin_adoption.md`
