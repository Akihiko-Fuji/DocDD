# ゲームルール試験項目 / Test Cases: Game Rules

- 文書ID: DOC-QA-041
- 最終更新日: 2026-03-23

| TC-ID | 観点 | 期待結果 | 対応文書 |
|---|---|---|---|
| TC-GR-001 | 1 ライン消去得点 | 40 × (level+1) が加算される | FR-206, DOC-SPC-023 |
| TC-GR-002 | 4 ライン消去得点 | 1200 × (level+1) が加算される | FR-206, DOC-SPC-023 |
| TC-GR-003 | ソフトドロップ得点 | 最後の連続距離のみ加算される | FR-206, DOC-SPC-023 |
| TC-GR-004 | A-TYPE レベル上昇 | 規定ライン到達で 1 レベル上昇する | FR-208, DOC-SPC-023 |
| TC-GR-005 | T-Spin 0 line | T-Spin 0 line 得点が適用される | FR-210, FR-211, DOC-SPC-023 |
| TC-GR-006 | T-Spin 1 line | T-Spin 1 line 得点が適用される | FR-210, FR-211, DOC-SPC-023 |
| TC-GR-007 | T-Spin 不成立 | 通常得点または加点なしとなる | FR-210, DOC-SPC-024 |
| TC-GR-008 | 出現不能ゲームオーバー | 新規出現失敗でゲームオーバーになる | FR-005, DOC-SPC-020 |
