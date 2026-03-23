# トレーサビリティマトリクス / Traceability Matrix

- 文書ID: DOC-REQ-016
- 文書名: トレーサビリティマトリクス / Traceability Matrix
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: BR を起点とし、その下流に UC / DM / SR / NSR / EXT / Internal Contract / TC の 7 つの主要追跡軸を持つ形で、上流意図から下流検証までを縦に追える状態を保つ
- 関連文書:
  - `docs/00_overview/01_project_charter.md`
  - `docs/01_requirements/11_scope_definition.md`
  - `docs/01_requirements/12_use_cases.md`
  - `docs/01_requirements/13_functional_requirements.md`
  - `docs/01_requirements/14_non_functional_requirements.md`
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/03_internal_design/31_domain_model.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/04_quality_assurance/41_test_cases_game_rules.md`
  - `docs/04_quality_assurance/42_test_cases_ui_input.md`
  - `docs/04_quality_assurance/43_test_cases_edge_conditions.md`

---

## 1. 本書の目的

本書は、DocDD の説明用サンプルとして、**上流の意図から下流のテストまでを一筆書きで辿れること**を明示するための文書である。

本書では、単なる FR 起点の対応表ではなく、BR を起点にその下流 7 軸を追う形で上流層と下流層を分けて整理する。

---

## 2. 追跡モデル

```text
BR -> UC -> DM -> SR / NSR -> EXT -> Internal Contract -> TC
```

- BR: 事業・プロジェクト上の目的
- UC: 利用者が達成したい代表行為
- DM: ドメイン概念とランタイム概念
- SR / NSR: 機能要求・非機能要求
- EXT: 外部仕様
- Internal Contract: 内部契約、モジュール責務、依存関係、公開インタフェース
- TC: 試験ケース

---

## 3. 上流層マトリクス

| トレース例 | BR | UC | DM | SR / NSR | EXT |
|---|---|---|---|---|---|
| TR-001 A-TYPE 開始 | `01_project_charter` の「DocDD 見本として主要フローを成立させる」 / `11` 4.1 | UC-001 | GameSession, ScoreState | FR-001, FR-002, FR-003, NFR-003 | `20` 6, `21` 6, `22` 5, `25` 7 |
| TR-002 ピース操作 | `11` 4.1, 4.2 | UC-002 | Board, CurrentPiece, InputSnapshot | FR-102, FR-103, FR-104, FR-105, FR-107, NFR-001, NFR-002 | `20` 8, `22` 3-7, `24` 5-9 |
| TR-003 T-Spin 採用 | `11` 6.3 | UC-002 | CurrentPiece, TSpinResult, ScoreState | FR-206, FR-210, FR-211, NFR-101, NFR-203 | `20` 8.6 / 11.4, `23` 4-5, `24` 10 |
| TR-004 一時停止と再開 | `11` 4.1, 4.4 | UC-003 | GameSession, PauseState, InputSnapshot | FR-108, FR-401, FR-402, FR-403, FR-405, NFR-003 | `21` 8, `22` 5-7, `25` 2-7 |
| TR-005 ゲームオーバー後の再試行 | `11` 4.1 | UC-004 | GameSession, ScoreState | FR-005, FR-006, FR-405, NFR-105 | `20` 7, `21` 9, `25` 5-7 |
| TR-006 非採用機能の明示 | `11` 5.2 | 関連 UC なし（制約） | Board, InputSnapshot | FR-212, NFR-206, NFR-203 | `20` 4.5, `22` 4 / 8 |

---

## 4. 下流層マトリクス

| トレース例 | EXT | Internal Contract / Design | 主テスト | 補助テスト |
|---|---|---|---|---|
| TR-001 A-TYPE 開始 | `20` 6, `21` 6, `22` 5 | `32` ST-SETUP-A, `34` input_mapper / state_controller / game_session | TC-UI-001, TC-UI-002 | - |
| TR-002 ピース操作 | `20` 8-9, `22` 3-7, `24` 5-9 | `32` PL-ACTIVE, `34` input_mapper / active_piece_service / board_rules | TC-EC-001, TC-EC-002, TC-EC-003 | TC-EC-004 |
| TR-003 T-Spin 採用 | `20` 8.6 / 11.4, `23` 4-5, `24` 10 | `32` PL-SCORE, `34` lock_resolver / tspin_detector / scoring_service | TC-GR-005, TC-GR-006 | TC-GR-007, TC-EC-007 |
| TR-004 一時停止と再開 | `21` 8, `22` 5-7, `25` 2-7 | `32` ST-PAUSE, `34` state_controller / game_session / renderer | TC-UI-004, TC-UI-005 | TC-EC-005, TC-EC-010 |
| TR-005 ゲームオーバー後の再試行 | `20` 7, `21` 9, `25` 5-7 | `32` ST-GAMEOVER, `34` spawn_service / state_controller / game_session | TC-GR-008, TC-UI-008 | TC-EC-006 |
| TR-006 非採用機能の明示 | `20` 4.5, `22` 4 / 8 | `34` input_mapper / renderer | TC-UI-007 | TC-EC-008 |

---

## 5. 代表機能の縦断トレース例

### 5.1 例1: T-Spin 採用
| 層 | 参照 |
|---|---|
| BR | `11_scope_definition.md` 6.3 |
| UC | UC-002 |
| DM | `31_domain_model.md` の `TSpinResult`, `ScoreState` |
| SR | FR-210, FR-211 |
| NSR | NFR-101, NFR-203 |
| EXT | `20` 11.4, `23` 4-5, `24` 10 |
| Internal Contract | `34_module_design.md` の `tspin_detector`, `scoring_service`, `lock_resolver` |
| TC | TC-GR-005, TC-GR-006, TC-GR-007, TC-EC-007 |

### 5.2 例2: 一時停止
| 層 | 参照 |
|---|---|
| BR | `11_scope_definition.md` 4.1 |
| UC | UC-003 |
| DM | `PauseState`, `GameSession`, `InputSnapshot` |
| SR | FR-401, FR-402, FR-403, FR-405 |
| NSR | NFR-003 |
| EXT | `21` 8, `22` 5-7, `25` 2-7 |
| Internal Contract | `state_controller`, `game_session`, `renderer` |
| TC | TC-UI-004, TC-UI-005, TC-EC-005, TC-EC-010 |

### 5.3 例3: Hard drop 非採用
| 層 | 参照 |
|---|---|
| BR | `11_scope_definition.md` 5.2 |
| UC | なし（制約事項） |
| DM | `InputSnapshot` |
| SR | FR-212 |
| NSR | NFR-206 |
| EXT | `20` 4.5, `22` 4 / 8 |
| Internal Contract | `input_mapper` は Hard drop を公開しない |
| TC | TC-UI-007, TC-EC-008 |

### 5.4 例4: A-TYPE のレベル進行
| 層 | 参照 |
|---|---|
| BR | `11_scope_definition.md` 4.1 |
| UC | UC-001, UC-002 |
| DM | `ScoreState`, `GameSession` |
| SR | FR-207, FR-208, FR-209 |
| NSR | NFR-101, NFR-105 |
| EXT | `20` 13, `23` 8-9 |
| Internal Contract | `scoring_service`, `level_progression_service`, `game_session` |
| TC | TC-GR-004 |

### 5.5 例5: ゲームオーバー後の再試行
| 層 | 参照 |
|---|---|
| BR | `11_scope_definition.md` 4.1 |
| UC | UC-004 |
| DM | `GameSession`, `ScoreState` |
| SR | FR-005, FR-006, FR-405 |
| NSR | NFR-105 |
| EXT | `20` 7, `21` 9, `25` 5-7 |
| Internal Contract | `spawn_service`, `state_controller`, `game_session` |
| TC | TC-GR-008, TC-UI-008, TC-EC-006 |

---

## 6. 運用ルール

1. 新規 FR / NFR を追加した場合は、最低 1 件の上流層トレースと 1 件の下流層トレースを更新する
2. 変更が Internal Contract に影響する場合は `34_module_design.md` を同時更新する
3. テストを追加した場合は、どの SR / NSR / EXT / Internal Contract を根拠に導出したか追記する
4. 非採用機能も、制約として追跡対象に含める

---

## 7. 変更履歴

- 2026-03-23: FR 中心の単層表から、上流層 / 下流層の二層トレーサビリティへ再構成
- 2026-03-23: T-Spin、一時停止、Hard drop 非採用、レベル進行、再試行の縦断例を追加
