# 7軸トレーサビリティ対応表 / Traceability Axes Map

- 文書ID: DOC-OVW-006
- 最終更新日: 2026-03-23
- 目的: 一般的な V 字モデル / トレーサビリティ説明で用いられる 7 軸と、本プロジェクト文書群との対応関係を明示する

---

## 1. 本書の目的

本書は、一般的な V 字モデル / トレーサビリティ説明で用いられる 7 軸と、
本プロジェクトの文書群との対応関係を示す補助文書である。

本プロジェクトでは、要求・仕様・設計・試験を単一文書へ集約せず、役割ごとに分離して管理する。
そのため、外部説明やレビュー時に「7 軸のどこに何があるか」を即座に確認できるよう、本書を overview 系文書として用意する。

---

## 2. 対応表

| 7軸 | 本プロジェクトでの対応文書 |
|---|---|
| 顧客要件（Customer Requirements） | `docs/01_requirements/10_product_vision.md`, `docs/01_requirements/11_scope_definition.md`, `docs/01_requirements/12_use_cases.md` |
| システム要件（System Requirements） | `docs/01_requirements/13_functional_requirements.md`, `docs/01_requirements/14_non_functional_requirements.md`, `docs/01_requirements/15_acceptance_criteria.md` |
| アーキテクチャ設計（Architectural Design） | `docs/03_internal_design/30_architecture_design.md`, `docs/03_internal_design/31_domain_model.md` |
| 詳細設計（Detailed Design） | `docs/03_internal_design/32_state_machine_design.md` ～ `docs/03_internal_design/39_interface_contract.md` |
| ソースコード（Implementation） | `src/` |
| 単体 / 結合テスト（Unit / Integration Test） | `docs/04_quality_assurance/40_test_strategy.md`, `docs/04_quality_assurance/41_test_cases_game_rules.md`, `docs/04_quality_assurance/42_test_cases_ui_input.md`, `docs/04_quality_assurance/43_test_cases_edge_conditions.md` |
| システムテスト（System Test） | `docs/01_requirements/15_acceptance_criteria.md`, `docs/01_requirements/16_traceability_matrix.md`, `docs/04_quality_assurance/44_performance_test_plan.md` |

---

## 3. 補足

### 3.1 外部仕様の位置付け

本プロジェクトでは、`docs/02_external_spec/20` ～ `26` を
**システム要件を外部可視挙動へ具体化した文書群**として扱う。

したがって、7 軸上では「システム要件そのもの」と「その具体化としての外部仕様」を分離して読むのが適切である。
要件の正本は `13` ～ `15` だが、レビューや試験設計では `20` ～ `26` を併読する前提とする。

### 3.2 詳細設計の位置付け

本プロジェクトでは、詳細設計を単一文書ではなく、
状態・データ・モジュール・描画・入力・異常系・内部契約へ分割して管理する。

そのため、詳細設計軸は `32` ～ `39` をまとめて扱う。
特定観点のみ確認したい場合でも、設計判断は関連文書との整合を前提に行う。

### 3.3 トレーサビリティマトリクスの位置付け

`docs/01_requirements/16_traceability_matrix.md` は、上記各軸の縦断追跡を支える管理文書である。
個別軸の正本を置き換えるものではなく、
要求・仕様・設計・試験の対応関係を横断的に確認するための入口として扱う。

---

## 4. 利用ガイド

- 7 軸の全体対応を最初に把握したい場合は、本書を overview の入口補助として読む
- 正本の要求定義を確認したい場合は `docs/01_requirements/13` ～ `15` を優先して読む
- 外部仕様の具体像を確認したい場合は `docs/02_external_spec/20` ～ `26` を続けて参照する
- 設計判断や実装根拠を確認したい場合は `docs/03_internal_design/30` ～ `39` と `src/` を対応付けて読む
- 検証観点を確認したい場合は `docs/04_quality_assurance/40` ～ `44` と `docs/01_requirements/16_traceability_matrix.md` を併読する
