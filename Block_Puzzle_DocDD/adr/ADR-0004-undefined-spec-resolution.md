# ADR-0004: 仕様未定義項目の確定 / Resolution of Undefined Specification Items

- ADR-ID: ADR-0004
- 最終更新日: 2026-03-24
- 状態: Accepted
- 目的: DocDD レビューで抽出された「実装判断に直結する未定義・委譲先未記載」の項目について、Game Boy 版テトリスを基準として一括確定し、追加文書への追跡先を記録する
- 関連文書:
  - `docs/02_external_spec/24a_piece_shape_spawn_spec.md`（新規）
  - `docs/02_external_spec/23a_timing_constants_spec.md`（新規）
  - `docs/02_external_spec/23b_display_limits_spec.md`（新規）
  - `specs/schemas/config_schema.json`（修正）
  - `src/vibe_coding/vibe_code_tetris.py`（比較用成果物として注記更新）
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/26_save_replay_config_spec.md`

---

## 1. 背景

本プロジェクトのドキュメントセットをレビューした結果、以下の項目が「委譲先未記載」または「他文書で未定義」の状態にあり、複数の実装者・テスト設計者が独自に値を決めた場合に文書間矛盾が生じるリスクが確認された。

1. 全ピースの `occupied_offsets`（回転別セル座標）が存在しない
2. ピース出現座標（spawn origin）が存在しない
3. T-Spin 判定の「回転中心」と対角 4 点の座標が不明確
4. ARE（出現待ち）フレーム数が未定義
5. ライン消去演出待ちフレーム数が未定義
6. ソフトドロップ速度の計算式が存在しない（「1/3G 相当」のみ記載）
7. `config_schema.json` で keyboard_bindings と gamepad_bindings が両方 `required` であり、仕様文書の意図と矛盾している
8. LINES・LEVEL の表示桁数と上限が未定義
9. SCORE の内部保持値キャップ判断が設計委譲のまま
10. replay の frame=0 がどの状態を指すかが未定義
11. `src/vibe_coding/vibe_code_tetris.py`（旧 `superminimum.py`）の座標系・BOARD_H が文書と不整合（注記なし）

---

## 2. 決定

各項目を Game Boy 版テトリスを基準として以下の通り確定する。

### 2.1 ピース形状・出現座標・T-Spin 回転中心

新規文書 `24a_piece_shape_spawn_spec.md` を `docs/02_external_spec/` に追加し、以下を正本として定義した。

| 項目 | 確定内容 |
|---|---|
| occupied_offsets | 全 7 種 × 全 4 回転の `(dx, dy)` リスト |
| 出現 origin 座標 | 全 7 種の `(origin_x, origin_y)` = 横中央・上端付近 |
| 出現時 rotation | 全種 `0`（North 姿勢）|
| T-Spin 回転中心 | T ピースの `origin` と一致。対角 4 点は `(origin ± 1, origin ± 1)` |

### 2.2 ARE・ライン消去演出待ち・ソフトドロップ速度

新規文書 `23a_timing_constants_spec.md` を `docs/02_external_spec/` に追加し、以下を確定した。

| 定数 | 確定値 | 根拠 |
|---|---|---|
| ソフトドロップ速度 | 3 frames/row（1/3G @ 60fps） | 60 fps における 1/3G の計算値 |
| ARE（通常） | 10 frames | Game Boy 版実機計測の中間値 |
| ライン消去演出待ち | 20 frames | Game Boy 版実機での消去演出時間 |
| ARE（消去あり合計） | 30 frames | `LINE_CLEAR_DELAY + ARE_FRAMES` |

### 2.3 SCORE 内部上限・LINES/LEVEL 表示桁数・replay frame=0

新規文書 `23b_display_limits_spec.md` を `docs/02_external_spec/` に追加し、以下を確定した。

| 項目 | 確定内容 |
|---|---|
| SCORE 内部上限 | 999,999 でキャップ（表示と内部で一致させ replay 再現性を保つ） |
| LINES 表示上限 | 3 桁 / 最大 999 / 超過時は `999` 固定 |
| LEVEL 表示上限 | 2 桁 / 最大 20（仕様上限と一致） |
| replay frame=0 | GameSession 生成直後の最初のフレーム（ST-PLAY 開始時点） |

### 2.4 config_schema.json の修正

`specs/schemas/config_schema.json` を以下の通り修正した。

- 変更前: `required` 配列に `keyboard_bindings` と `gamepad_bindings` の両方が含まれていた
- 変更後: `oneOf` 分岐を追加し、`input_interface=keyboard` のときのみ `keyboard_bindings` 必須、`input_interface=gamepad` のときのみ `gamepad_bindings` 必須とした
- 根拠: `26_save_replay_config_spec.md` §3.2「`input_interface` に応じて一方のみを参照する」との矛盾を解消するため

### 2.5 `src/vibe_coding/vibe_code_tetris.py` への注記更新

`src/vibe_coding/vibe_code_tetris.py`（旧 `superminimum.py`）の先頭コメントに以下を反映した。

- SHAPES の座標系が文書（`board[y][x]`、x 右増加・y 下増加）と異なる旨
- `BOARD_H` は公式仕様に合わせて `18` へ修正済みである旨（比較用成果物であり仕様正本ではない旨）

---

## 3. 理由

- Game Boy 版テトリスの公開情報（The Tetris Wiki、実機解析）に基づく数値を採用した
- replay の再現条件に影響する定数（ARE、消去待ち、ソフトドロップ速度、SCORE 上限）は内部まで一貫させることで `26_save_replay_config_spec.md` §4.3 の再現条件を確実に満たせるようにした
- config_schema.json の修正は仕様変更ではなく、仕様文書の意図への schema の追従である

---

## 4. 影響範囲

| 影響先 | 変更種別 |
|---|---|
| `24_piece_rotation_collision_spec.md` | 本 ADR で定義した `24a_piece_shape_spawn_spec.md` を関連文書として追加する |
| `23_scoring_level_spec.md` | 本 ADR で定義した `23a_timing_constants_spec.md` および `23b_display_limits_spec.md` を関連文書として追加する |
| `26_save_replay_config_spec.md` | `23b_display_limits_spec.md` §6 の replay frame=0 定義を関連文書として追加する |
| `33_data_model.md` | `24a_piece_shape_spawn_spec.md` を `occupied_offsets` の数値正本として参照先に追加する |
| `40_test_strategy.md` | 本 ADR により確定した数値定数を基準としたテストケース追加を要検討 |
| `41_test_cases_game_rules.md` | ピース出現座標・ARE フレームのテストケースを追加する |

---

## 5. 未解決項目

本 ADR では扱わなかった項目（DocDD 上は Minor として分類）を以下に残す。

- Game Boy 版の randomizer アルゴリズムの詳細実装（再抽選ロジック）は `spawn_service` 実装時に別 ADR または設計文書で確定する
- `src/vibe_coding/vibe_code_tetris.py` の SHAPES 定義と文書座標系の完全な整合（注記で留めた）

---

## 6. 変更履歴

- 2026-03-24: `superminimum.py` の `src/vibe_coding/vibe_code_tetris.py` へのリネーム、および比較成果物としての位置づけ更新に合わせて参照先を更新。`BOARD_H` が 18 に修正済みである記述へ同期
- 2026-03-24: DocDD レビュー指摘の未定義 11 項目を受け、3 つの補完仕様文書・schema 修正・注記追加を一括確定
