# 文書更新チェックリスト / Document Update Checklist

- 文書ID: DOC-MGT-056
- 最終更新日: 2026-03-24
- 目的: 変更要求を受けたとき、DocDD の更新漏れを防ぐための実行用 checklist を提供する
- 関連文書:
  - `docs/05_project_management/53_change_management.md`
  - `docs/05_project_management/54_issue_management.md`
  - `docs/04_quality_assurance/45_definition_of_done.md`

## 1. 使い方
- 変更着手前に変更種別を 1 つ以上選ぶ
- 影響文書確認欄を埋め、未該当は `N/A` とする
- 変更完了前に traceability / record / DoD の確認を行う

## 2. 変更種別チェック
- [ ] requirement
- [ ] spec
- [ ] design
- [ ] test
- [ ] record
- [ ] bug
- [ ] enhancement

## 3. 影響文書確認欄
### 3.1 Requirements
- [ ] `11_scope_definition.md`
- [ ] `13_functional_requirements.md`
- [ ] `14_non_functional_requirements.md`
- [ ] `15_acceptance_criteria.md`
- [ ] `16_traceability_matrix.md`

### 3.2 External Spec
- [ ] `20_game_rules_spec.md`
- [ ] `21_ui_screen_spec.md`
- [ ] `22_input_operation_spec.md`
- [ ] `23_scoring_level_spec.md`
- [ ] `24_piece_rotation_collision_spec.md`
- [ ] `25_pause_gameover_resume_spec.md`
- [ ] `26_save_replay_config_spec.md`
- [ ] `docs/03_internal_design/27_runtime_flowchart_mermaid.md`

### 3.3 Internal Design
- [ ] `30_architecture_design.md`
- [ ] `31_domain_model.md`
- [ ] `32_state_machine_design.md`
- [ ] `33_data_model.md`
- [ ] `34_module_design.md`
- [ ] `35_rendering_design.md`
- [ ] `36_input_timing_design.md`
- [ ] `37_error_handling_policy.md`
- [ ] `38_runtime_state_transition_mermaid.md`

### 3.4 QA / Fixtures
- [ ] `40_test_strategy.md`
- [ ] `41_test_cases_game_rules.md`
- [ ] `42_test_cases_ui_input.md`
- [ ] `43_test_cases_edge_conditions.md`
- [ ] `44_performance_test_plan.md`
- [ ] `45_definition_of_done.md`
- [ ] `46_test_fixtures_catalog.md`
- [ ] `docs/00_overview/05_document_maturity_matrix.md`

### 3.5 Records / Management
- [ ] `53_change_management.md`
- [ ] `54_issue_management.md`
- [ ] `55_risk_register.md`
- [ ] `60_decision_log.md`
- [ ] `61_change_log.md`
- [ ] `62_review_log.md`

## 4. 変更波及確認
- [ ] affected docs を issue / PR / change note に列挙した
- [ ] affected test cases を列挙した
- [ ] affected ADR / decision log を列挙した
- [ ] schema / sample / examples 更新要否を確認した
- [ ] diagram 更新要否を確認した

## 5. Traceability / DoD 確認
- [ ] `16_traceability_matrix.md` 更新要否を確認した
- [ ] DoD への影響を確認した
- [ ] 未成熟文書のまま残す場合は `05_document_maturity_matrix.md` を更新した
- [ ] fixture 追加時は `46_test_fixtures_catalog.md` を更新した

## 6. 受入観点
- requirement / spec / design / test / record の変更種別ごとに実務で使えること
- 関連文書確認、traceability、ADR、schema/sample、DoD の確認欄が揃っていること
- 人間レビューでも AI 変更でも同じ手順で使えること

## 7. 変更履歴
- 2026-03-24: `56_document_update_checklist.md` として project management 配下へ再配置し、参照先文書を更新
