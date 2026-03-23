# トレーサビリティマトリクス / Traceability Matrix

- 文書ID: DOC-REQ-016
- 文書名: トレーサビリティマトリクス / Traceability Matrix
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: BR を起点に、その下流に UC / DM / SR / NSR / EXT / Internal Contract / TC の主要追跡軸を持つ形で、上流意図から下流検証までを縦に追える状態を保つ

---

## 1. 追跡モデル

```text
BR -> UC -> DM -> SR / NSR -> EXT -> Internal Contract -> TC
```

---

## 2. 上流層マトリクス

| トレース例 | BR | UC | DM | SR / NSR | EXT |
|---|---|---|---|---|---|
| TR-001 A-TYPE 開始 | `01_project_charter` 7, `11` 4 | UC-001 | GameSession, ScoreState | FR-001, FR-002, FR-003, NFR-003 | `20` 6, `21` 6, `22` 5, `25` 7 |
| TR-002 ピース操作 | `11` 4.1 | UC-002 | Board, CurrentPiece, InputSnapshot | FR-102, FR-103, FR-104, FR-105, FR-107, NFR-001, NFR-002 | `20` 8, `22` 3-6, `24` 5-9 |
| TR-003 NEXT 表示切替 | `04_reference_baseline_and_deltas` 2, `11` 4.1 | UC-002 | NextQueue, UiState, InputSnapshot | FR-109, FR-110, FR-303, FR-304, NFR-005, NFR-304 | `20` 4.4 / 12.1, `21` 7.2, `22` 3-5 |
| TR-004 T-Spin 採用 | `11` 6.3 | UC-002 | CurrentPiece, TSpinResult, ScoreState | FR-206, FR-210, FR-211, NFR-101, NFR-203 | `20` 11.6, `23` 3-4, `24` 10 |
| TR-005 一時停止と再開 | `11` 4.1 | UC-003 | GameSession, PauseState, InputSnapshot | FR-401, FR-402, FR-403, FR-404, NFR-003 | `21` 8, `22` 5-7, `25` 2-7 |
| TR-006 非採用機能の明示 | `11` 5 | 関連 UC なし | Board, InputSnapshot | FR-212, NFR-206, NFR-303 | `20` 4.5, `22` 8 |

---

## 3. 下流層マトリクス

| トレース例 | EXT | Internal Contract / Design | 主テスト | 補助テスト |
|---|---|---|---|---|
| TR-001 A-TYPE 開始 | `20` 6, `21` 6, `22` 5 | `32` ST-SETUP-A, `34` input_mapper / state_controller / game_session | TC-UI-001, TC-UI-002 | - |
| TR-002 ピース操作 | `20` 8-9, `22` 3-7, `24` 5-9 | `32` PL-ACTIVE, `34` input_mapper / active_piece_service / board_rules | TC-EC-001, TC-EC-002, TC-EC-003 | TC-EC-004 |
| TR-003 NEXT 表示切替 | `20` 12.1, `21` 7.2, `22` 3-5 | `32` ST-PLAY / PL-ACTIVE, `34` ui_state / input_mapper / renderer | TC-UI-006, TC-UI-007 | TC-EC-009 |
| TR-004 T-Spin 採用 | `20` 11.6, `23` 3-4, `24` 10 | `32` PL-SCORE, `34` lock_resolver / tspin_detector / scoring_service | TC-GR-005, TC-GR-006 | TC-GR-007, TC-EC-007 |
| TR-005 一時停止と再開 | `21` 8, `22` 5-7, `25` 2-7 | `32` ST-PAUSE, `34` state_controller / game_session / renderer | TC-UI-004, TC-UI-005 | TC-EC-005 |
| TR-006 非採用機能の明示 | `20` 4.5, `22` 8 | `34` input_mapper / renderer | TC-UI-008 | TC-EC-008 |

---

## 4. 変更履歴

- 2026-03-23: SELECT/NEXT 表示切替の縦断トレースを追加
- 2026-03-23: 上流層 / 下流層の二層トレーサビリティへ再構成
