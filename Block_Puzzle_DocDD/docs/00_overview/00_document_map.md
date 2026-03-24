# 文書一覧 / Document Map

- 文書ID: DOC-OVW-000
- 文書名: 文書一覧 / Document Map
- 最終更新日: 2026-03-24
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 本プロジェクトで管理する文書の役割、参照順序、更新責任範囲を明確化する

---

## 1. この文書の目的

本書は、落下ブロックゲームを題材とした**ドキュメント駆動開発（Document-Driven Development / DocDD）見本プロジェクト**において、各文書の役割、参照順序、更新責務、およびレビュー観点を定義する入口文書である。

本プロジェクトでは、コードの前に以下の順序で認識を固定する。

1. 何を作るかをプロジェクト文書で定義する
2. 何を満たすべきかを要求文書で定義する
3. ユーザーから見える挙動を外部仕様で定義する
4. 内部責務と状態遷移を設計文書で定義する
5. 要求と仕様をどう検証するかを品質文書で定義する
6. 変更理由とレビュー結果を記録文書へ残す

---

## 2. プロジェクトの位置付け

本プロジェクトは、公開可能な題材を用いて、実務に近い粒度で DocDD の流れを示すことを目的とする。

題材は**Game Boy 版テトリスをベースラインとする落下ブロックゲーム**であり、以下を前提に扱う。

- 主軸は A-TYPE とし、B-TYPE は参照仕様として併記する
- 盤面は 10×18、NEXT は 1 個、Hold なし、Hard drop なしとする
- SELECT による NEXT 表示切替は Game Boy 版準拠の補助仕様として扱う
- 7-bag は採用せず、Game Boy 系ランダマイザ方針を維持する
- T-Spin は**本プロジェクト独自拡張**として追加する
- 画像・キャラクタ・演出素材は独自制作物を使用する
- 実装対象は PC 上で動作する単体アプリケーションとする
- 想定描画解像度は 640×576 とし、PC 利用を前提とした固定基準解像度とする
- 主題はゲーム作品の差別化ではなく、**文書整備の一貫性と追跡可能性**にある

---

## 3. 文書体系の全体像

本プロジェクトの文書は以下の 6 系統で構成する。

1. **Overview**: 前提、用語、参照元差分、文書読解順を示す
2. **Requirements**: スコープ、要求、受入条件、トレーサビリティを示す
3. **External Specification**: ユーザーから見えるゲーム挙動、UI、操作、得点、状態を示す
4. **Internal Design**: 状態遷移、モジュール責務、データ構造、描画/入力処理方針を示す
5. **Quality Assurance**: テスト方針、テストケース、DoD を示す
6. **Records / Management**: 意思決定、変更、レビュー、リスク、運営方針を記録する

---

## 4. コア 10 文書

本プロジェクトでは、以下の 10 文書を基準文書とし、DocDD の最小骨格として最優先で整備する。

| 区分 | ファイル | 役割 |
|---|---|---|
| Overview | `docs/00_overview/00_document_map.md` | 文書群の入口と読解順を定義する |
| Overview | `docs/00_overview/01_project_charter.md` | 目的、成功条件、成果物、レビュー基準を定義する |
| Requirements | `docs/01_requirements/11_scope_definition.md` | 対象/非対象と Game Boy 基準との差分境界を定義する |
| Requirements | `docs/01_requirements/13_functional_requirements.md` | 機能要求を ID 付きで定義する |
| Requirements | `docs/01_requirements/14_non_functional_requirements.md` | 応答性、再現性、追跡可能性など品質要求を定義する |
| External Spec | `docs/02_external_spec/20_game_rules_spec.md` | ルール全体、ゲーム進行、数値基準の外部仕様を定義する |
| External Spec | `docs/02_external_spec/21_ui_screen_spec.md` | 画面群、表示要素、画面遷移、画面別受理入力を定義する |
| External Spec | `docs/02_external_spec/24_piece_rotation_collision_spec.md` | 回転、衝突、失敗条件、T-Spin 前提を定義する |
| Internal Design | `docs/03_internal_design/32_state_machine_design.md` | 上位状態とプレイ中サブ状態の設計を定義する |
| QA | `docs/04_quality_assurance/40_test_strategy.md` | 文書起点のテスト導出方針を定義する |

---

## 5. 今回のレビューで補強した重点論点

今回の改修では、コア 10 文書に対して以下の不足を重点修正対象とした。

1. **Spec-Driven の不足**
   - SELECT の扱い、B-TYPE の参照粒度、Game Boy 速度表などが暗黙だった
   - ルール順序と画面仕様の接続が弱かった
2. **Acceptance-Driven の不足**
   - 文書単体でレビュー完了判定できる観点が薄い箇所があった
   - 「どこが Game Boy 準拠で、どこが独自拡張か」が一目で判断しづらかった
3. **Diagram-Driven の不足**
   - 状態図やフローチャートと本文の同期条件が弱かった
   - 図からテストケースへ落とせる粒度が不足していた

これを受け、各コア文書に以下を追加・強化する。

- Game Boy 基準値・暗黙仕様の明文化
- 受入観点の明文化
- 状態・責務・図面の同期ルール
- 変更影響の参照先

---

## 6. 文書ごとの役割一覧

### 6.1 Overview

| ファイル | 役割 |
|---|---|
| `docs/00_overview/00_document_map.md` | 本文書。全文書の一覧、役割、参照順序、更新方針を示す |
| `docs/00_overview/01_project_charter.md` | プロジェクトの目的、背景、成果物、成功条件、レビュー方針を定義する |
| `docs/00_overview/02_glossary.md` | 用語集。Board、Spawn、Lock、ARE、Soft Drop などを定義する |
| `docs/00_overview/03_assumptions_and_constraints.md` | 前提条件、プラットフォーム、技術制約、運用制約を整理する |
| `docs/00_overview/04_reference_baseline_and_deltas.md` | Game Boy 版基準として継承した要素と独自拡張・除外を整理する |
| `docs/00_overview/05_document_maturity_matrix.md` | 文書成熟度と利用可否を明示する |
| `docs/00_overview/06_traceability_axes_map.md` | 一般的な 7 軸と本プロジェクト文書群の対応関係を示す |

### 6.2 Requirements

| ファイル | 役割 |
|---|---|
| `docs/01_requirements/10_product_vision.md` | プロダクト視点の目標と価値を示す |
| `docs/01_requirements/11_scope_definition.md` | 対象範囲 / 非対象範囲 / 参照仕様の扱いを定義する |
| `docs/01_requirements/12_use_cases.md` | 利用者視点の代表ユースケースを整理する |
| `docs/01_requirements/13_functional_requirements.md` | 機能要求を要求 ID 付きで定義する |
| `docs/01_requirements/14_non_functional_requirements.md` | 非機能要求を定義する |
| `docs/01_requirements/15_acceptance_criteria.md` | 受入基準を定義する |
| `docs/01_requirements/16_traceability_matrix.md` | 要求、仕様、設計、テストの対応関係を管理する |

### 6.3 External Specification

| ファイル | 役割 |
|---|---|
| `docs/02_external_spec/20_game_rules_spec.md` | ルール全体、進行、B-TYPE 参照条件、速度・得点・終了条件を定義する |
| `docs/02_external_spec/21_ui_screen_spec.md` | 画面構成、表示要素、画面遷移、NEXT 表示方針を定義する |
| `docs/02_external_spec/22_input_operation_spec.md` | 入力手段、論理入力、SELECT 含む状態別入力を定義する |
| `docs/02_external_spec/23_scoring_level_spec.md` | スコア計算、レベル上昇、速度表を定義する |
| `docs/02_external_spec/23a_timing_constants_spec.md` | ARE、ライン消去待ち、ソフトドロップのフレーム定数を定義する |
| `docs/02_external_spec/23b_display_limits_spec.md` | SCORE/LINES/LEVEL の表示・内部上限と replay frame=0 起点を定義する |
| `docs/02_external_spec/24_piece_rotation_collision_spec.md` | 回転、衝突、失敗、T-Spin 前提を定義する |
| `docs/02_external_spec/24a_piece_shape_spawn_spec.md` | ピース形状 occupied_offsets と spawn origin を定義する |
| `docs/02_external_spec/25_pause_gameover_resume_spec.md` | ポーズ、再開、ゲームオーバー、再試行を定義する |
| `docs/02_external_spec/26_save_replay_config_spec.md` | 設定・保存・リプレイ仕様と schema 正本方針を定義する |

### 6.4 Internal Design

| ファイル | 役割 |
|---|---|
| `docs/03_internal_design/27_runtime_flowchart_mermaid.md` | ランタイム処理順と主要分岐を Mermaid で可視化する |
| `docs/03_internal_design/30_architecture_design.md` | システム全体構成と責務分割を定義する |
| `docs/03_internal_design/31_domain_model.md` | ドメイン概念とその関係を定義する |
| `docs/03_internal_design/32_state_machine_design.md` | システム状態と遷移条件を定義する |
| `docs/03_internal_design/33_data_model.md` | 内部データ・保存データ構造を定義する |
| `docs/03_internal_design/34_module_design.md` | モジュール責務と内部契約を定義する |
| `docs/03_internal_design/35_rendering_design.md` | 描画方式、再描画責務、視認性要件を定義する |
| `docs/03_internal_design/36_input_timing_design.md` | 入力受付タイミング、押下継続、リピート挙動を定義する |
| `docs/03_internal_design/37_error_handling_policy.md` | 異常系ポリシーを定義する |
| `docs/03_internal_design/38_runtime_state_transition_mermaid.md` | 状態遷移を Mermaid で可視化する |
| `docs/03_internal_design/39_interface_contract.md` | モジュール間のデータ契約と前後条件を一覧化する |

### 6.5 Quality Assurance

| ファイル | 役割 |
|---|---|
| `docs/04_quality_assurance/40_test_strategy.md` | 品質確認の全体方針を定義する |
| `docs/04_quality_assurance/41_test_cases_game_rules.md` | ルール、得点、進行の試験項目を定義する |
| `docs/04_quality_assurance/42_test_cases_ui_input.md` | UI と入力操作の試験項目を定義する |
| `docs/04_quality_assurance/43_test_cases_edge_conditions.md` | 境界条件や非採用機能の試験項目を定義する |
| `docs/04_quality_assurance/44_performance_test_plan.md` | 性能確認方針を定義する |
| `docs/04_quality_assurance/45_definition_of_done.md` | 文書・実装・テストを含む完了条件を定義する |
| `docs/04_quality_assurance/46_test_fixtures_catalog.md` | 再利用可能な盤面・入力・開始状態 fixture を定義する |

### 6.6 Records / Management

意思決定、変更、レビュー、WBS、マイルストーン、リスクを管理する。特に仕様差分や独自拡張は `60_decision_log.md` / `61_change_log.md` / `62_review_log.md` を正本とする。

補助運用文書として、`46_test_fixtures_catalog.md`・`05_document_maturity_matrix.md`・`56_document_update_checklist.md` を追加し、試験再現性、文書成熟度、変更手順の実務運用を補強する。

---

## 7. 推奨参照順序

### 7.1 最低限の把握順序

1. `00_document_map.md`
2. `01_project_charter.md`
3. `04_reference_baseline_and_deltas.md`
4. `11_scope_definition.md`
5. `13_functional_requirements.md`
6. `14_non_functional_requirements.md`

### 7.2 仕様把握順序

1. `20_game_rules_spec.md`
2. `23_scoring_level_spec.md`
3. `23a_timing_constants_spec.md`
4. `23b_display_limits_spec.md`
5. `22_input_operation_spec.md`
6. `21_ui_screen_spec.md`
7. `24_piece_rotation_collision_spec.md`
8. `24a_piece_shape_spawn_spec.md`
9. `25_pause_gameover_resume_spec.md`

### 7.3 設計把握順序

1. `32_state_machine_design.md`
2. `34_module_design.md`
3. `31_domain_model.md`
4. 図補助文書

### 7.4 品質確認順序

1. `40_test_strategy.md`
2. `15_acceptance_criteria.md`
3. 各テストケース文書
4. `16_traceability_matrix.md`

---

## 8. 文書間の基本関係

```text
Project Charter
    ↓
Reference Baseline / Scope Definition
    ↓
Functional / Non-Functional Requirements
    ↓
External Specifications
    ↓
Internal Design
    ↓
Test Strategy / Test Cases
    ↓
Traceability Matrix / Review Log / Change Log
```

より具体的には以下を意識する。

- `11_scope_definition.md` は対象/非対象と基準仕様との差分境界を定める
- `13_functional_requirements.md` は必要機能を定義する
- `14_non_functional_requirements.md` は品質制約を定義する
- `20`〜`25` 系仕様文書は外部挙動へ落とす
- `32_state_machine_design.md` は実装可能な状態遷移へ落とす
- `40_test_strategy.md` は要求と仕様からテスト導出方法を定める
- `16_traceability_matrix.md` は要求からテストまでの縦断追跡を保証する

---

## 9. 文書作成・更新ルール

### 9.1 基本原則

- 実装より先に、関係する要求・仕様・設計文書を確認する
- 実装で仕様を決めない。先に文書を更新する
- DocDD 実装成果物は `src/DocDD_coding/` へ配置し、`src/vibe_coding/vibe_code_tetris.py` は比較成果物として分離管理する
- 仕様変更時は影響文書を同一変更で更新する
- 文書更新を伴わない仕様変更は未完了とみなす

### 9.2 変更時の最小確認セット

ピース回転仕様を変更した場合、最低でも以下を確認する。

- `24_piece_rotation_collision_spec.md`
- `20_game_rules_spec.md`
- `22_input_operation_spec.md`
- `32_state_machine_design.md`
- `40_test_strategy.md`
- 関連テストケース文書
- `16_traceability_matrix.md`
- `60_decision_log.md` または ADR

### 9.3 記録の残し方

- 大きな設計判断は ADR に残す
- 文書方針や仕様境界の採否は `60_decision_log.md` に残す
- レビュー指摘と対応は `62_review_log.md` に残す
- ユーザー影響のある変更は `61_change_log.md` に残す

### 9.4 評価視点

- **Spec-Driven**: コア 10 文書を正本として、不足仕様を暗黙にしない
- **Acceptance-Driven**: 各主要文書にレビュー可能な受入観点を持たせる
- **Diagram-Driven**: 図を本文の要約として扱い、図と本文を同一変更で同期する

---

## 10. 文書ヘッダ規則

各文書の先頭には原則として以下を記載する。

- 文書ID
- 文書名
- 最終更新日
- 対象プロジェクト
- 目的
- 関連文書
- 必要に応じて変更履歴

---

## 11. DocDD の考え方

本プロジェクトにおける DocDD の基本思想は以下である。

- 文書は実装の付属物ではなく成果物の一部である
- 要求・仕様・設計・テストを分離して管理する
- 文書間の関係を追跡可能にする
- 変更理由を記録する
- 実装だけでなく判断経緯も再利用可能な形で残す

---

## 12. 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-03-23 | コア 10 文書のレビュー観点、Game Boy 基準の補強点、参照順序を再整理 |
| 2026-03-23 | 初版作成 |
