# データモデル設計 / Data Model Design

- 文書ID: DOC-DSN-033
- 最終更新日: 2026-03-24
- 関連文書:
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/02_external_spec/24a_piece_shape_spawn_spec.md`
  - `docs/02_external_spec/23a_timing_constants_spec.md`
  - `docs/02_external_spec/23b_display_limits_spec.md`
  - `docs/02_external_spec/26_save_replay_config_spec.md`
  - `docs/03_internal_design/31_domain_model.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `specs/schemas/config_schema.json`
  - `specs/schemas/replay_schema.json`

## 1. 目的
本書は、ゲーム進行・保存・再現に必要な主要データ構造の正本設計を定義する。単なる型一覧ではなく、**実装判断がぶれないように表現方式、不変条件、外部 schema との対応**を明文化する。

## 2. データモデリング原則
1. 盤面・現在ピース・NEXT・得点状態を分離し、責務境界を明確にする
2. 外部公開形式（Config / Replay）と内部実行形式（GameSession など）は分けて設計する
3. フレーム番号、座標系、回転値の単位を曖昧にしない
4. schema が存在する型は対応関係を表で示し、どちらが正本かを明記する

## 3. 座標系と盤面表現
### 3.1 盤面の正本表現
- Board は **row-major の 2 次元配列** を正本表現とする
- インデックスは `board[y][x]` とし、`x` が列、`y` が行を表す
- 可視盤面は 10 列 × 18 行とし、`0 <= x <= 9`, `0 <= y <= 17` を可視領域とする
- 空セルは `Empty`、占有セルは `I/O/T/S/Z/J/L/GarbageReserved` などの列挙値で表す想定とする

### 3.2 原点と方向
- 原点 `(0, 0)` は**可視盤面左上**とする
- `x` は右方向に増加、`y` は下方向に増加する
- 出現判定では、可視領域の上側にある予約領域は持たず、**出現位置が可視盤面内へ収まること**を前提とする
- したがって、Game Boy 基準の出現失敗は「初期配置が可視盤面の固定済みセルと衝突するか」で判定する

### 3.3 代替表現の扱い
- 衝突判定や描画最適化のために派生表現（occupied cell list など）を持ってもよい
- ただし更新正本は常に Board の row-major 表現とし、派生表現はキャッシュ扱いとする

## 4. 主要データ構造
### 4.1 BoardCell
| 項目 | 型 | 説明 |
|---|---|---|
| `kind` | enum | 空/固定済み種別 |
| `occupied` | boolean | そのセルが埋まっているか |
| `lock_origin` | optional enum | どのピース由来で固定されたか |

不変条件:
- `occupied == false` のとき `kind == Empty` でなければならない
- `occupied == true` のセルは可視盤面内にのみ存在する

### 4.2 PieceState
| 項目 | 型 | 説明 |
|---|---|---|
| `piece_type` | enum | I/O/T/S/Z/J/L |
| `origin_x` | integer | 基準位置 x |
| `origin_y` | integer | 基準位置 y |
| `rotation` | integer | 0/1/2/3 |
| `occupied_offsets` | tuple list | 基準位置からの相対占有座標 |
| `last_successful_action` | enum | Spawn/Move/Rotate/SoftDrop/None |

不変条件:
- `rotation` は `0,1,2,3` のいずれかに限る
- `occupied_offsets` は 4 セル分を保持し、各セルは同一座標を重複しない（正本値は `24a_piece_shape_spawn_spec.md`）
- `occupied_offsets` を `origin_x`, `origin_y` に加算した結果は、評価対象時点で盤面境界判定可能でなければならない

### 4.3 CurrentPiece と PieceState の関係
- Active piece は `CurrentPiece` という別名を用いてよいが、**構造正本は `PieceState` を共有**する
- `CurrentPiece` は `PieceState + fall_timer + lock_pending` のような実行時補助属性を含むラッパとして扱う
- これにより、固定前の現在ピースと replay / debug 用スナップショットで同一形状表現を再利用できる

### 4.4 NextQueue
| 項目 | 型 | 説明 |
|---|---|---|
| `visible_next` | enum | UI に表示される次ピース |
| `supply_buffer` | optional enum/list | 実装都合で保持する次供給情報 |

方針:
- 外部仕様上は NEXT 1 個表示が正本である
- 内部設計では将来拡張や乱数供給責務分離のため `NextQueue` という名称を許容する
- ただし version 1 の意味論は**常に visible_next 1 個のみが外部契約**であり、複数 preview を示唆してはならない

### 4.5 ScoreState
| 項目 | 型 | 説明 |
|---|---|---|
| `score` | integer | 現在スコア |
| `lines` | integer | 累積消去ライン数 |
| `level` | integer | 現在レベル |
| `last_award_reason` | enum | Single/Double/Triple/Tetris/TSpin0/TSpin1... |

不変条件:
- `score >= 0`, `lines >= 0`, `level >= 0`
- `level` 更新は `23_scoring_level_spec.md` の基準に従う

### 4.6 GameSession
| 項目 | 型 | 説明 |
|---|---|---|
| `session_id` | string/uuid | セッション識別子 |
| `state` | enum | `ST-*` 上位状態 |
| `play_substate` | optional enum | `PL-*` サブ状態 |
| `board` | 2D array | 盤面正本 |
| `current_piece` | optional CurrentPiece | 操作中ピース |
| `next_queue` | NextQueue | 次ピース管理 |
| `score_state` | ScoreState | 得点系状態 |
| `input_snapshot` | InputSnapshot | 現フレーム入力 |
| `frame` | integer | セッション開始からのフレーム番号 |
| `pause_reason` | optional enum | 手動停止など |
| `randomizer_seed` | integer | 乱数再現用 seed |

不変条件:
- `state != ST-PLAY` のとき `play_substate` は `None` でもよい
- `frame` は 0 起算の単調増加整数とする（frame=0 の起点は `23b_display_limits_spec.md` §6 に従う）
- `state == ST-PLAY` のとき `board`, `next_queue`, `score_state` は必須とする

### 4.7 InputSnapshot
| 項目 | 型 | 説明 |
|---|---|---|
| `frame` | integer | 取得フレーム |
| `pressed_buttons` | set | 当該フレームで成立した論理入力集合 |
| `source` | enum | keyboard/gamepad/replay |

不変条件:
- `pressed_buttons` の要素は `Left/Right/Down/A/B/START/SELECT` のみに限る
- `frame` は `GameSession.frame` と一致する

### 4.8 TSpinResult
| 項目 | 型 | 説明 |
|---|---|---|
| `is_tspin` | boolean | T-Spin 判定結果 |
| `corner_count` | integer | 対角占有数 |
| `line_clear_count` | integer | 同時消去数 |
| `award_reason` | enum | TSpin0/TSpin1/.../None |

### 4.9 Config
`26_save_replay_config_spec.md` と `config_schema.json` に従う。内部では `config.ini` の読込結果として以下の構造を持つ。

| 項目 | 型 | 説明 |
|---|---|---|
| `version` | integer | 形式バージョン |
| `start_level` | integer | 既定開始レベル |
| `input_interface` | enum | `keyboard` または `gamepad` |
| `keyboard_bindings` | object | 論理入力 -> 物理キーコード |
| `gamepad_bindings` | object | 論理入力 -> 物理ボタン名 |
| `randomizer_seed` | optional integer | テスト用 seed |

### 4.10 ReplayFrame
| 項目 | 型 | 説明 |
|---|---|---|
| `frame` | integer | 入力発生フレーム |
| `buttons` | string list | 当該フレームで発生した論理入力 |

不変条件:
- `frame >= 0`
- `buttons` は空配列を許容してもよいが、sample では有意味入力のみを記録する
- frame は昇順とし、同一 frame が重複する場合は事前正規化して 1 レコードへ統合する

## 5. schema / sample 対応表
| 設計型 | 対応 schema / sample | 正本 | 補足 |
|---|---|---|---|
| `Config` | `specs/schemas/config_schema.json`, `specs/examples/config_sample_01.ini` | schema | sample は INI 実ファイル例 |
| `ReplayFrame` | `specs/schemas/replay_schema.json#properties.inputs.items`, `specs/examples/replay_sample_01.json` | schema | replay の 1 要素 |
| replay aggregate | `specs/schemas/replay_schema.json`, `specs/examples/replay_sample_01.json` | schema | 文書上は aggregate 名を固定しない |
| `InputSnapshot` | replay 再生時に `ReplayFrame` から変換 | 設計文書 | 外部 schema へ直接は露出しない |

## 6. 実装判断ガイド
- 盤面更新は常に Board 正本へ反映してから描画・判定へ渡す
- T-Spin 判定は `PieceState.last_successful_action` と `TSpinResult` を組み合わせて導出する
- `NextQueue` は内部で queue 名を使ってよいが、UI と外部仕様では NEXT 1 個表示だけを見せる
- replay 再生時は `ReplayFrame -> InputSnapshot` 変換を 1 箇所へ集約し、通常入力系と同一処理へ流す
- `config.ini` の入力設定は、起動時に `Config` へ正規化してから `input_mapper` へ渡す

## 7. Acceptance-Driven 受入観点
- Board 正本表現、座標系、CurrentPiece / PieceState 関係、NextQueue 意味論が本文だけで判断できること
- 不変条件が実装レビュー時のチェック項目として使える粒度になっていること
- Config / Replay 系データと schema/sample の対応が追跡できること
- 盤面、入力、得点、再現性に関する曖昧さが残っていないこと
