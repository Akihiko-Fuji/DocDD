# ゲームルール試験項目 / Test Cases: Game Rules

- 文書ID: DOC-QA-041
- 最終更新日: 2026-03-23

| TC-ID | 観点 | 前提条件 | 入力 / 操作 | 実施手順 | 期待状態遷移 | pass 条件 | 関連 FR / NFR / EXT / Design |
|---|---|---|---|---|---|---|---|
| TC-GR-001 | 1 ライン消去得点 | A-TYPE プレイ中、レベル 0、単一ラインのみ完成する盤面 | 必要位置へピースを落下・固定 | 1. 対象盤面を構成する 2. 1 ライン完成で固定する 3. SCORE を確認する | `PL-CLEAR -> PL-SCORE -> PL-NEXT` | 40 × (level+1) = 40 点が加算され、LINES が 1 増える | FR-204, FR-206, FR-207 / NFR-101 / DOC-SPC-020, DOC-SPC-023 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-002 | 4 ライン消去得点 | A-TYPE プレイ中、レベル 0、4 行同時消去が可能な盤面 | I ピース等で 4 行同時消去 | 1. 4 行消去直前盤面を構成する 2. ピースを固定する 3. SCORE, LINES を確認する | `PL-CLEAR -> PL-SCORE -> PL-NEXT` | 1200 点が加算され、LINES が 4 増える | FR-204, FR-206, FR-207 / NFR-101 / DOC-SPC-020, DOC-SPC-023 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-003 | ソフトドロップ得点 | A-TYPE プレイ中、連続 3 マスのソフトドロップで固定可能 | Down を連続入力して固定 | 1. 通常落下では即固定しない盤面を用意する 2. Down を 3 マス連続入力する 3. 固定後の SCORE を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-SCORE` | 最後の連続ソフトドロップ距離のみが加点される | FR-105, FR-206 / NFR-101 / DOC-SPC-020, DOC-SPC-023 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-004 | A-TYPE レベル上昇 | 開始レベル 0、LINES=9 のプレイ状態 | 1 ライン消去を発生させる | 1. 開始レベル 0 で 9 ライン消去済み状態を作る 2. 1 ライン消去する 3. LEVEL と落下速度指標を確認する | `PL-CLEAR -> PL-SCORE -> PL-NEXT` | LEVEL が 1 に上昇し、以後の重力設定がレベル 1 扱いになる | FR-207, FR-208, FR-209 / NFR-101, NFR-105 / DOC-SPC-020, DOC-SPC-023 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-005 | T-Spin 0 line | T ピース、最終成立操作が回転、対角 3 箇所以上占有、消去行なし | A または B で回転して固定 | 1. T-Spin 0 line 盤面を構成する 2. 回転成功後に固定する 3. 得点表示を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-SCORE` | T-Spin 0 line の専用得点が適用され、通常得点表が使われない | FR-210, FR-211 / NFR-101, NFR-203 / DOC-SPC-020, DOC-SPC-023, DOC-SPC-024 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-006 | T-Spin 1 line | T ピース、最終成立操作が回転、T-Spin 成立かつ 1 行消去 | A または B で回転して固定 | 1. T-Spin 1 line 盤面を構成する 2. 回転成功後に固定する 3. SCORE と LINES を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-CLEAR -> PL-SCORE` | T-Spin 1 line 得点が適用され、LINES が 1 増える | FR-204, FR-206, FR-210, FR-211 / NFR-101, NFR-203 / DOC-SPC-020, DOC-SPC-023, DOC-SPC-024 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-007 | T-Spin 不成立 | T ピース固定盤面、対角占有 2 箇所以下または最終操作が回転でない | 左右移動またはソフトドロップ後に固定 | 1. 不成立条件の盤面を構成する 2. 回転以外を最終成立操作にする 3. 固定して得点を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-SCORE` | T-Spin と判定されず、通常得点または加点なしとなる | FR-206, FR-210 / NFR-101 / DOC-SPC-023, DOC-SPC-024 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-008 | 出現不能ゲームオーバー | 出現位置が固定済みブロックで塞がれている | 次ピース出現を発生させる | 1. 出現位置を塞いだ盤面を作る 2. 現在ピースを固定して次出現へ進める 3. 状態を確認する | `PL-NEXT -> PL-END-CHECK -> ST-GAMEOVER` | 新規出現失敗によりゲームオーバーへ遷移し、最終値が固定表示される | FR-005, FR-405 / NFR-105 / DOC-SPC-020, DOC-SPC-025 / DOC-DSN-032, DOC-DSN-034 |
