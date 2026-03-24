# 7軸トレーサビリティ対応表 / Traceability Axes Map

- 文書ID: DOC-OVW-006
- 文書名: 7軸トレーサビリティ対応表 / Traceability Axes Map
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 一般的な V 字モデル / トレーサビリティ説明で用いられる 7 軸と、本プロジェクト文書群との対応関係を明示し、外部説明と内部文書体系の接続を補助する

---

## 1. 本書の位置付け

本書は、overview 系文書の一つとして、一般的な V 字モデル / トレーサビリティ説明で用いられる 7 軸と、本プロジェクトの文書群との対応関係を示す補助文書である。

本プロジェクトでは、要求・仕様・設計・試験を単一文書へ集約せず、役割ごとに分離して管理する。  
そのため、外部説明やレビュー時に「7 軸のどこに何があるか」を即座に確認できるよう、本書を overview の入口補助として用意する。

本書は対応関係を整理するための **Reference 文書** であり、個別軸の正本を置き換えるものではない。  
実装判断・レビュー判断・変更判断は、各軸に対応する正本文書を参照して行う。

---

## 2. 7軸対応表

| 7軸 | 本プロジェクトでの対応文書 | 補足 |
|---|---|---|
| 顧客要件（Customer Requirements） | `docs/01_requirements/10_product_vision.md`<br>`docs/01_requirements/11_scope_definition.md`<br>`docs/01_requirements/12_use_cases.md` | 誰に何を提供するか、対象/非対象、主要利用像を定義する |
| システム要件（System Requirements） | `docs/01_requirements/13_functional_requirements.md`<br>`docs/01_requirements/14_non_functional_requirements.md`<br>`docs/01_requirements/15_acceptance_criteria.md` | 要求を機能要求・非機能要求・受入条件へ落とし込む正本 |
| アーキテクチャ設計（Architectural Design） | `docs/03_internal_design/30_architecture_design.md`<br>`docs/03_internal_design/31_domain_model.md` | システム境界、責務分割、主要概念、集約境界を定義する |
| 詳細設計（Detailed Design） | `docs/03_internal_design/32_state_machine_design.md` ～ `docs/03_internal_design/39_interface_contract.md` | 状態、データ、モジュール、描画、入力、異常系、内部契約を分割管理する |
| ソースコード（Implementation） | `src/DocDD_coding/`<br>`src/vibe_coding/vibe_code_tetris.py` | DocDD 正本実装は `src/DocDD_coding/`。`vibe_code_tetris.py` は短いリクエスト由来の比較成果物であり、正本実装とは分離する |
| 単体 / 結合テスト（Unit / Integration Test） | `docs/04_quality_assurance/40_test_strategy.md`<br>`docs/04_quality_assurance/41_test_cases_game_rules.md`<br>`docs/04_quality_assurance/42_test_cases_ui_input.md`<br>`docs/04_quality_assurance/43_test_cases_edge_conditions.md` | 設計どおりに動くかを検証する試験方針・試験仕様 |
| システムテスト（System Test） | `docs/01_requirements/15_acceptance_criteria.md`<br>`docs/01_requirements/16_traceability_matrix.md`<br>`docs/04_quality_assurance/44_performance_test_plan.md` | 要求を満たしているかを受入・性能・縦断追跡の観点で確認する |

---

## 3. 読み方と補足

### 3.1 外部仕様の位置付け

本プロジェクトでは、`docs/02_external_spec/20_game_rules_spec.md` ～ `docs/02_external_spec/26_save_replay_config_spec.md` を、**システム要件を外部可視挙動へ具体化した文書群**として扱う。

したがって、7 軸上では `13` ～ `15` をシステム要件の正本としつつ、レビュー、設計、試験設計では `20` ～ `26` を併読する前提とする。  
本書では簡潔さを優先して 7 軸表の主対応からは外しているが、実運用上はシステム要件と詳細設計の間をつなぐ重要な層である。

### 3.2 詳細設計の位置付け

本プロジェクトでは、詳細設計を単一文書ではなく、以下の観点へ分割して管理する。

- `32_state_machine_design.md`: 状態遷移
- `33_data_model.md`: データ構造
- `34_module_design.md`: モジュール責務
- `35_rendering_design.md`: 描画設計
- `36_input_timing_design.md`: 入力・時間軸設計
- `37_error_handling_policy.md`: 異常系設計
- `38_runtime_state_transition_mermaid.md`: 状態図補助
- `39_interface_contract.md`: 内部契約

そのため、7 軸上の「詳細設計」は `32` ～ `39` を束として読む。  
特定観点のみ確認したい場合でも、設計判断は関連文書との整合を前提に行う。

### 3.3 トレーサビリティマトリクスの位置付け

`docs/01_requirements/16_traceability_matrix.md` は、各軸の正本を置き換える文書ではなく、  
要求・仕様・設計・試験の対応関係を **縦断的に確認するための管理文書** である。

本書が「一般的な 7 軸」と「本プロジェクト文書群」の対応を示すのに対し、  
`16_traceability_matrix.md` は、本プロジェクト内部で実際に運用する追跡モデルを管理する。

### 3.4 一般的な 7軸と本プロジェクト内部トレースの関係

本プロジェクト内部では、一般的な 7 軸をそのまま運用キーにはせず、  
より実装判断に使いやすい形として、以下の追跡軸を採用している。

```text
BR -> UC -> DM -> SR / NSR -> EXT -> Internal Contract -> TC
```

- 7 軸: 外部説明、教育、レビュー時の全体把握に向く
- BR / UC / DM / SR / NSR / EXT / Internal Contract / TC: 本プロジェクト内部の縦断追跡に向く

本書は前者の見取り図であり、`16_traceability_matrix.md` は後者の運用正本である。

---

## 4. 利用ガイド

- 7 軸と文書群の全体対応を最初に把握したい場合は、本書を overview の入口補助として読む
- 文書群の参照順序と役割を確認したい場合は `docs/00_overview/00_document_map.md` を併読する
- 実装判断に使ってよい文書かどうかを確認したい場合は `docs/00_overview/05_document_maturity_matrix.md` を併読する
- 正本の要求定義を確認したい場合は `docs/01_requirements/13_functional_requirements.md` ～ `15_acceptance_criteria.md` を優先して読む
- 外部仕様の具体像を確認したい場合は `docs/02_external_spec/20_game_rules_spec.md` ～ `26_save_replay_config_spec.md` を続けて参照する
- 設計判断や実装根拠を確認したい場合は `docs/03_internal_design/30_architecture_design.md` ～ `39_interface_contract.md` と `src/DocDD_coding/` を対応付けて読む
- `src/vibe_coding/vibe_code_tetris.py` は比較対象として参照し、仕様適合判断の一次根拠にはしない
- 検証観点を確認したい場合は `docs/04_quality_assurance/40_test_strategy.md` ～ `44_performance_test_plan.md` と `docs/01_requirements/16_traceability_matrix.md` を併読する

---

## 5. 受入観点

- 一般的な 7 軸と本プロジェクト文書群の対応が一目で分かること
- 各軸の正本がどこか、補助文書がどこかを誤読しにくいこと
- 外部仕様、詳細設計、トレーサビリティマトリクスの位置付けが本文で読めること
- overview 文書として、文書体系の入口補助に使えること

---

## 6. 変更履歴

- 2026-03-23: `06_traceability_axes_map.md` を新設し、一般的な 7 軸と本プロジェクト文書群の対応関係を整理
