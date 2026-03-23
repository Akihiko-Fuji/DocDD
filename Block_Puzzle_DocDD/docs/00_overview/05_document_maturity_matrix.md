# 文書成熟度マトリクス / Document Maturity Matrix

- 文書ID: DOC-OVW-005
- 最終更新日: 2026-03-24
- 目的: 各文書の成熟度と利用目的を明示し、未完成と予約仕様を区別できるようにする

## 1. 成熟度定義
| 成熟度 | 意味 | 実装判断に使ってよいか |
|---|---|---|
| `Stable` | 当面の正本として維持され、実装判断に直接使える | Yes |
| `Reference` | 正本補助。本文理解や基準確認に使う | Conditional |
| `Reserved` | 将来拡張用に最低構造のみ固定 | Limited |
| `Draft` | 方向性はあるが今後厚くする前提 | Caution |
| `Skeleton` | 骨格のみ。単独で判断してはいけない | No |

## 2. 主要文書マトリクス
| 文書 | 目的 | 成熟度 | 実装判断に使ってよいか | 次に厚くすべき項目 |
|---|---|---|---|---|
| `00_document_map.md` | 入口、役割整理 | Stable | Yes | 変更時に追加文書反映 |
| `11_scope_definition.md` | 対象/非対象範囲 | Stable | Yes | B-TYPE 対象化条件 |
| `13_functional_requirements.md` | 機能要求 | Stable | Yes | 将来拡張 FR の段階化 |
| `14_non_functional_requirements.md` | 非機能要求 | Stable | Yes | replay 永続化時の品質条件 |
| `20_game_rules_spec.md` | 外部ルール仕様 | Stable | Yes | B-TYPE 詳細化時の分離 |
| `21_ui_screen_spec.md` | 画面仕様 | Stable | Yes | 保存 UI 採用時の画面追加 |
| `24_piece_rotation_collision_spec.md` | 回転・衝突 | Stable | Yes | 実装検証結果反映 |
| `26_save_replay_config_spec.md` | 保存/再現予約仕様 | Reserved | Limited | 永続化タイミング、version 戦略 |
| `docs/03_internal_design/27_runtime_flowchart_mermaid.md` | 処理順図 | Reference | Conditional | 実装名との同期維持 |
| `32_state_machine_design.md` | 状態設計 | Stable | Yes | B-TYPE 予約状態の扱い |
| `33_data_model.md` | データ構造設計 | Stable | Yes | enum 詳細と validation 規約 |
| `34_module_design.md` | モジュール責務 | Stable | Yes | 実装契約粒度の追加 |
| `40_test_strategy.md` | QA 方針 | Stable | Yes | automation 境界の詳細化 |
| `41_test_cases_game_rules.md` | ルール試験仕様 | Draft | Yes | 実施結果の蓄積 |
| `42_test_cases_ui_input.md` | UI/入力試験仕様 | Draft | Yes | usability 記録欄の蓄積 |
| `43_test_cases_edge_conditions.md` | 境界試験仕様 | Draft | Yes | replay ベース手順の具体化 |
| `45_definition_of_done.md` | 完了条件 | Stable | Yes | フェーズ別 DoD 派生 |
| `46_test_fixtures_catalog.md` | fixture 正本 | Draft | Yes | 外部ファイル化規約 |
| `docs/05_project_management/56_document_update_checklist.md` | 実行用 checklist | Stable | Yes | 自動化導線 |
| `54_issue_management.md` | 課題運用 | Stable | Yes | 運用実績例の追記 |
| `55_risk_register.md` | リスク運用 | Stable | Yes | 指標化・レビュー履歴 |

## 3. 運用ルール
- `Reserved`, `Draft`, `Skeleton` の文書は、単独で仕様確定に使わず上位正本文書と組み合わせて参照する
- 成熟度を変更したときは `61_change_log.md` または `62_review_log.md` に記録する
- `Skeleton` が残る場合は DoD の未達理由として明示する

## 4. 受入観点
- 「薄い文書」が未完成なのか意図的な予約なのかを一目で判断できること
- 実装判断に使ってよい文書かどうかが明示されていること
- 次に厚くすべき項目がレビューの起点になること

## 5. 変更履歴
- 2026-03-24: `05_document_maturity_matrix.md` として overview 配下へ再配置し、成熟度マトリクスを文書入口側へ移動
