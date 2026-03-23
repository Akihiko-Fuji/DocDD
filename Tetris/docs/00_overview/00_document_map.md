# 文書一覧 / Document Map

- 文書ID: DOC-OVW-000
- 文書名: 文書一覧 / Document Map
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 本プロジェクトで管理する文書の役割、参照順序、更新責任範囲を明確化する

---

## 1. この文書の目的

本書は、落下ブロックゲームを題材とした**ドキュメント駆動開発（Document-Driven Development / DocDD）見本プロジェクト**において、各文書の役割と相互関係を定義するための文書である。

本プロジェクトでは、単にコードを書くのではなく、以下の順序を重視する。

1. 何を作るかを定義する
2. 何を満たすべきかを要求として定義する
3. 外から見た振る舞いを仕様として定義する
4. 内部構造を設計として定義する
5. テスト観点を定義する
6. 変更履歴と意思決定を記録する

本書は、その全体像を示す入口文書である。

---

## 2. プロジェクトの位置付け

本プロジェクトは、公開可能な題材を用いて、実務に近い粒度でDocDDの流れを示すことを目的とする。

題材は**テトリス系の落下ブロックゲーム**であるが、以下の前提で扱う。

- 操作感および基本ルールの基準は、**Game Boy版テトリスを参照元のひとつ**として設計する
- 主軸は A-TYPE とし、B-TYPE は参考仕様として扱う
- 10×18 盤面、NEXT 1個、Hold なし、Hard drop なしを固定条件とする
- T-Spin は本プロジェクト独自拡張として採用する
- 画像・キャラクタ・演出素材は独自制作物を使用する
- 実装対象はPC上で動作する単体アプリケーションとする
- 実装言語は、**コードがコンパクトで見通しが良いこと**を重視して選定する
- ただし、本プロジェクトの主題はコード技巧ではなく、**DocDD手法と文書整備の一貫性**にある

---

## 3. 文書体系の全体像

本プロジェクトの文書は、以下の6系統で構成する。

1. **Overview**  
   文書全体の入口、用語、前提、制約を示す

2. **Requirements**  
   何を作るか、何を満たすべきかを示す

3. **External Specification**  
   ユーザーから見える振る舞いとルールを示す

4. **Internal Design**  
   内部構造、状態遷移、モジュール責務を示す

5. **Quality Assurance**  
   テスト方針と品質確認方法を示す

6. **Records / Management**  
   意思決定、変更履歴、レビュー結果を記録する

---

## 4. ディレクトリ構成

```text
project-root/
├─ README.md
├─ docs/
│  ├─ 00_overview/
│  │  ├─ 00_document_map.md
│  │  ├─ 01_project_charter.md
│  │  ├─ 02_glossary.md
│  │  └─ 03_assumptions_and_constraints.md
│  │
│  ├─ 01_requirements/
│  │  ├─ 10_product_vision.md
│  │  ├─ 11_scope_definition.md
│  │  ├─ 12_use_cases.md
│  │  ├─ 13_functional_requirements.md
│  │  ├─ 14_non_functional_requirements.md
│  │  ├─ 15_acceptance_criteria.md
│  │  └─ 16_traceability_matrix.md
│  │
│  ├─ 02_external_spec/
│  │  ├─ 20_game_rules_spec.md
│  │  ├─ 21_ui_screen_spec.md
│  │  ├─ 22_input_operation_spec.md
│  │  ├─ 23_scoring_level_spec.md
│  │  ├─ 24_piece_rotation_collision_spec.md
│  │  ├─ 25_pause_gameover_resume_spec.md
│  │  └─ 26_save_replay_config_spec.md
│  │
│  ├─ 03_internal_design/
│  │  ├─ 30_architecture_design.md
│  │  ├─ 31_domain_model.md
│  │  ├─ 32_state_machine_design.md
│  │  ├─ 33_data_model.md
│  │  ├─ 34_module_design.md
│  │  ├─ 35_rendering_design.md
│  │  ├─ 36_input_timing_design.md
│  │  └─ 37_error_handling_policy.md
│  │
│  ├─ 04_quality_assurance/
│  │  ├─ 40_test_strategy.md
│  │  ├─ 41_test_cases_game_rules.md
│  │  ├─ 42_test_cases_ui_input.md
│  │  ├─ 43_test_cases_edge_conditions.md
│  │  ├─ 44_performance_test_plan.md
│  │  └─ 45_definition_of_done.md
│  │
│  ├─ 05_project_management/
│  │  ├─ 50_development_policy.md
│  │  ├─ 51_work_breakdown_structure.md
│  │  ├─ 52_milestones.md
│  │  ├─ 53_change_management.md
│  │  ├─ 54_issue_management.md
│  │  └─ 55_risk_register.md
│  │
│  └─ 06_records/
│     ├─ 60_decision_log.md
│     ├─ 61_change_log.md
│     ├─ 62_review_log.md
│     └─ 63_meeting_notes.md
│
├─ adr/
│  ├─ ADR-0001-game-loop-model.md
│  ├─ ADR-0002-randomizer-policy.md
│  └─ ADR-0003-input-buffer-policy.md
│
├─ specs/
│  ├─ examples/
│  │  ├─ replay_sample_01.json
│  │  └─ config_sample_01.yaml
│  └─ schemas/
│     ├─ replay_schema.json
│     └─ config_schema.json
│
└─ src/
```

---

## 5. 優先制作対象（今回のコア文書）

本プロジェクトでは、まず以下の文書を優先制作対象とする。

- docs/00_overview/00_document_map.md
- docs/00_overview/01_project_charter.md
- docs/01_requirements/11_scope_definition.md
- docs/01_requirements/13_functional_requirements.md
- docs/01_requirements/14_non_functional_requirements.md
- docs/02_external_spec/20_game_rules_spec.md
- docs/02_external_spec/21_ui_screen_spec.md
- docs/02_external_spec/24_piece_rotation_collision_spec.md
- docs/03_internal_design/32_state_machine_design.md
- docs/04_quality_assurance/40_test_strategy.md

これらをコア10文書と位置付け、DocDDの骨格を先に成立させる。

---

## 6. 文書ごとの役割一覧

### 6.1 Overview

| ファイル | 役割 |
|---|---|
| docs/00_overview/00_document_map.md | 本文書。全文書の一覧、役割、参照順序、更新方針を示す。プロジェクトの入口として機能する |
| docs/00_overview/01_project_charter.md | プロジェクトの目的、背景、成果物、対象読者を定義する。「なぜこのプロジェクトを行うのか」を示す |
| docs/00_overview/02_glossary.md | 用語集。ピース、盤面、スポーン、ロック、ホールド等の用語を定義する。文書間の語義ブレを防ぐ |
| docs/00_overview/03_assumptions_and_constraints.md | 前提条件と制約を整理する。対応プラットフォーム、対象外範囲、技術制約などを記載する |

### 6.2 Requirements

| ファイル | 役割 |
|---|---|
| docs/01_requirements/10_product_vision.md | 製品として何を目指すかを示す。プロジェクトチャーターよりも、プロダクト志向で記述する |
| docs/01_requirements/11_scope_definition.md | 対象範囲 / 非対象範囲を定義する。「どこまで作るか」「どこから先は作らないか」を明確にする |
| docs/01_requirements/12_use_cases.md | 利用者視点での代表的な利用場面を定義する。例: ゲーム開始、ピース操作、一時停止、設定変更 |
| docs/01_requirements/13_functional_requirements.md | 機能要求を一覧化する。システムが提供すべき機能を、要求ID付きで定義する |
| docs/01_requirements/14_non_functional_requirements.md | 非機能要求を定義する。操作応答性、再現性、保守性、可読性、移植性などを扱う |
| docs/01_requirements/15_acceptance_criteria.md | 受入条件を定義する。「何をもって満たしたと判断するか」を明確にする |
| docs/01_requirements/16_traceability_matrix.md | 要求、仕様、設計、テストの対応関係を管理する。DocDDの追跡可能性を担保する中核文書 |

### 6.3 External Specification

| ファイル | 役割 |
|---|---|
| docs/02_external_spec/20_game_rules_spec.md | ゲームルール全体の外部仕様を定義する。盤面、落下、固定、ライン消去、ゲームオーバー条件などを扱う |
| docs/02_external_spec/21_ui_screen_spec.md | 画面構成、表示要素、画面遷移を定義する。タイトル、プレイ画面、ポーズ、リザルト等を整理する |
| docs/02_external_spec/22_input_operation_spec.md | 入力手段と操作割当を定義する。キーボード操作や各入力の意味を整理する |
| docs/02_external_spec/23_scoring_level_spec.md | スコア計算、レベル上昇、難易度変化を定義する。プレイ結果に関する数値仕様を明文化する |
| docs/02_external_spec/24_piece_rotation_collision_spec.md | ピース回転と衝突判定の外部仕様を定義する。壁際、床際、他ブロック接触時の扱いを明確化する |
| docs/02_external_spec/25_pause_gameover_resume_spec.md | ポーズ、再開、ゲームオーバー、リトライの仕様を定義する |
| docs/02_external_spec/26_save_replay_config_spec.md | 設定保存、リプレイ保存、ロード対象を定義する。永続化対象の外部仕様を扱う |

### 6.4 Internal Design

| ファイル | 役割 |
|---|---|
| docs/03_internal_design/30_architecture_design.md | システム全体構成と責務分割を定義する。入力、ゲームロジック、描画、保存などの分担を整理する |
| docs/03_internal_design/31_domain_model.md | ドメイン概念とその関係を定義する。Board、Piece、NextQueue、GameSession、TSpinResult などを整理する |
| docs/03_internal_design/32_state_machine_design.md | システム状態と遷移条件を定義する。タイトル、プレイ中、ポーズ、ゲームオーバー等の遷移を明記する |
| docs/03_internal_design/33_data_model.md | 内部データ構造と保存データ構造を定義する。設定データ、リプレイデータ等を扱う |
| docs/03_internal_design/34_module_design.md | モジュール単位の責務と境界を定義する。実装ファイル分割の基準として用いる |
| docs/03_internal_design/35_rendering_design.md | 描画方式、再描画タイミング、表示責務を定義する |
| docs/03_internal_design/36_input_timing_design.md | 入力受付タイミング、押下継続、リピート挙動を定義する |
| docs/03_internal_design/37_error_handling_policy.md | 異常系の扱い方針を定義する。不正入力、壊れた設定、保存失敗時の方針を扱う |

### 6.5 Quality Assurance

| ファイル | 役割 |
|---|---|
| docs/04_quality_assurance/40_test_strategy.md | 品質確認の全体方針を定義する。何を、どの観点で、どう検証するかを示す |
| docs/04_quality_assurance/41_test_cases_game_rules.md | ゲームルールに関する試験項目を定義する |
| docs/04_quality_assurance/42_test_cases_ui_input.md | UIおよび入力操作に関する試験項目を定義する |
| docs/04_quality_assurance/43_test_cases_edge_conditions.md | 境界条件や例外的状況に関する試験項目を定義する |
| docs/04_quality_assurance/44_performance_test_plan.md | 性能観点の確認方針を定義する。フレーム安定性、長時間動作等を扱う |
| docs/04_quality_assurance/45_definition_of_done.md | 完了条件を定義する。実装完了ではなく、文書・テスト・記録まで含めた完了条件を扱う |

### 6.6 Project Management

| ファイル | 役割 |
|---|---|
| docs/05_project_management/50_development_policy.md | 開発ルール全般を定義する。変更時の文書更新原則、レビュー方針等を扱う |
| docs/05_project_management/51_work_breakdown_structure.md | 作業分解構成を定義する。進捗管理と分担整理の基礎とする |
| docs/05_project_management/52_milestones.md | マイルストーンを定義する。フェーズ区切りを明確にする |
| docs/05_project_management/53_change_management.md | 仕様変更や設計変更の管理方法を定義する |
| docs/05_project_management/54_issue_management.md | 課題、バグ、改善要求の管理方法を定義する |
| docs/05_project_management/55_risk_register.md | 想定リスクと対応方針を定義する |

### 6.7 Records

| ファイル | 役割 |
|---|---|
| docs/06_records/60_decision_log.md | 日々の判断・採否・理由を記録する。ADRより軽量な記録もここに残す |
| docs/06_records/61_change_log.md | バージョン単位の変更履歴を記録する |
| docs/06_records/62_review_log.md | レビュー指摘、判断、対応結果を記録する |
| docs/06_records/63_meeting_notes.md | 打合せメモや検討記録を残す |

### 6.8 ADR

| ファイル | 役割 |
|---|---|
| adr/ADR-0001-game-loop-model.md | ゲームループ方式に関する意思決定を記録する |
| adr/ADR-0002-randomizer-policy.md | ピース出現順の方式に関する意思決定を記録する |
| adr/ADR-0003-input-buffer-policy.md | 入力バッファや入力解釈方針に関する意思決定を記録する |

ADRは、なぜその方式を選んだのかを残すための設計判断記録とする。

### 6.9 Specs

| ファイル | 役割 |
|---|---|
| specs/examples/replay_sample_01.json | リプレイデータのサンプルを格納する |
| specs/examples/config_sample_01.yaml | 設定ファイルのサンプルを格納する |
| specs/schemas/replay_schema.json | リプレイデータの形式定義を格納する |
| specs/schemas/config_schema.json | 設定ファイルの形式定義を格納する |

---

## 7. 参照順序

新規参画者、レビュー担当者、実装担当者は、原則として以下の順に参照する。

### 7.1 最低限の把握順序

1. 00_document_map.md
2. 01_project_charter.md
3. 11_scope_definition.md
4. 13_functional_requirements.md
5. 14_non_functional_requirements.md

### 7.2 仕様把握順序

1. 20_game_rules_spec.md
2. 21_ui_screen_spec.md
3. 24_piece_rotation_collision_spec.md

### 7.3 設計把握順序

1. 32_state_machine_design.md
2. 関連する内部設計文書

### 7.4 品質確認順序

1. 40_test_strategy.md
2. 対応する各テストケース文書
3. 16_traceability_matrix.md

---

## 8. 文書間の関係

本プロジェクトの基本的な関係は以下の通りである。

```
Project Charter
    ↓
Scope Definition
    ↓
Functional / Non-Functional Requirements
    ↓
External Specifications
    ↓
Internal Design
    ↓
Test Strategy / Test Cases
    ↓
Traceability Matrix / Review / Change Log
```

より具体的には、以下の対応を意識する。

- `11_scope_definition.md` は、何を対象とし何を対象外とするかを定める
- `13_functional_requirements.md` は、機能面の要求を定義する
- `14_non_functional_requirements.md` は、品質面の要求を定義する
- `20_game_rules_spec.md` などの仕様文書は、それら要求を具体的な振る舞いに落とす
- `32_state_machine_design.md` などの設計文書は、仕様を内部構造へ落とす
- `40_test_strategy.md` は、要求と仕様をどう検証するかの方針を定める
- `16_traceability_matrix.md` は、要求からテストまでのつながりを保証する

---

## 9. 文書作成・更新ルール

### 9.1 基本原則

- 実装より先に、関係する要求・仕様・設計文書を確認する
- 実装により仕様が変わるのではなく、仕様変更を明文化したうえで実装を変える
- 仕様変更時は、影響する文書を同時に更新する
- 文書更新を伴わない仕様変更は、原則として未完了とみなす

### 9.2 更新対象の考え方

たとえば、ピース回転仕様を変更した場合は、少なくとも以下を確認する。

- 24_piece_rotation_collision_spec.md
- 32_state_machine_design.md（必要に応じて）
- 40_test_strategy.md
- 関連テストケース文書
- 16_traceability_matrix.md
- 60_decision_log.md または ADR

### 9.3 記録の残し方

- 大きな設計判断は ADR に残す
- 比較的小さな判断は 60_decision_log.md に残す
- レビューでの指摘と対応は 62_review_log.md に残す
- ユーザー影響のある変更は 61_change_log.md に残す

---

## 10. 文書命名規則

### 10.1 ファイル名規則

- 形式: `番号_英語名.md`
- 例: `13_functional_requirements.md`

### 10.2 文書タイトル規則

- 見出しタイトルは日本語を基本とする
- 必要に応じて英語副題を併記する

### 10.3 文書ヘッダ推奨項目

各文書の先頭には、原則として以下を記載する。

- 文書ID
- 文書名
- 最終更新日
- 対象プロジェクト
- 目的
- 関連文書
- 更新履歴（必要に応じて）

---

## 11. 本プロジェクトにおけるDocDDの考え方

本プロジェクトでは、DocDDを以下のように位置付ける。

- 文書は成果物の付属物ではなく、成果物そのものの一部である
- 要求・仕様・設計・テストは分離して管理する
- 文書間の関係を追跡可能にする
- 変更理由を記録する
- 実装だけではなく、判断の経緯も再利用可能な形で残す

本プロジェクトの価値は、ゲーム完成そのものではなく、小規模題材でも実務に耐える文書構造を成立させられることにある。

---

## 12. 現時点の制作順序

本書の作成時点では、以下の順で文書を整備する。

1. 00_document_map.md
2. 01_project_charter.md
3. 11_scope_definition.md
4. 13_functional_requirements.md
5. 14_non_functional_requirements.md
6. 20_game_rules_spec.md
7. 21_ui_screen_spec.md
8. 24_piece_rotation_collision_spec.md
9. 32_state_machine_design.md
10. 40_test_strategy.md

必要に応じて、この後に周辺文書を拡張する。

---

## 13. 備考

- 本プロジェクトは公開可能なDocDD見本として整備する
- 実案件の守秘情報、実業務データ、実社内仕様は含めない
- ただし、文書の粒度、考え方、構造、追跡性は実務レベルを目指す

---

## 14. 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-03-23 | 初版作成 |