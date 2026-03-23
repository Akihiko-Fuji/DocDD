# UI・入力試験項目 / Test Cases: UI and Input

- 文書ID: DOC-QA-042
- 最終更新日: 2026-03-23

| TC-ID | 観点 | 期待結果 | 対応文書 |
|---|---|---|---|
| TC-UI-001 | タイトルから開始設定へ遷移 | START で開始設定へ進む | FR-001, DOC-SPC-021 |
| TC-UI-002 | 開始レベル変更 | 0～9 の範囲で変更できる | FR-002, DOC-SPC-021, DOC-SPC-022 |
| TC-UI-003 | プレイ画面に NEXT / SCORE / LINES / LEVEL 表示 | 必須表示が揃う | FR-303, DOC-SPC-021 |
| TC-UI-004 | START で一時停止 | プレイからポーズへ遷移する | FR-401, DOC-SPC-025 |
| TC-UI-005 | 一時停止から再開 | 停止前状態から復帰する | FR-403, DOC-SPC-025 |
| TC-UI-006 | SELECT 相当入力が進行へ影響しない | 盤面・状態に変化がない | FR-109, DOC-SPC-022 |
| TC-UI-007 | Hard drop 用入力が存在しない | 専用操作が提供されない | FR-212, DOC-SPC-022 |
| TC-UI-008 | ゲームオーバーから再試行 | START / A で開始設定へ戻る | FR-006, DOC-SPC-025 |
