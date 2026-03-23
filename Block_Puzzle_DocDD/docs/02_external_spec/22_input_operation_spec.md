# 入力操作仕様 / Input Operation Specification

- 文書ID: DOC-SPC-022
- 最終更新日: 2026-03-23
- 関連文書:
  - `20_game_rules_spec.md`
  - `21_ui_screen_spec.md`
  - `24_piece_rotation_collision_spec.md`
  - `25_pause_gameover_resume_spec.md`
  - `32_state_machine_design.md`

## 1. 目的
Game Boy 版基準の論理入力を、PC 実装へ写像する外部仕様を定義する。

## 2. 基本方針
1. ユーザー向け説明では Game Boy 系の論理ボタン名を保持する
2. 実装では PC キーへ対応付ける
3. 入力は状態依存で有効 / 無効を切り替える
4. Hard drop や Hold など、採用しない入力は明示的に不採用とする
5. PC 実装で補助キーを設ける場合も、論理入力との対応関係を明示する

## 3. 論理入力
| 論理入力 | 役割 | PC 推奨割当例 | 備考 |
|---|---|---|---|
| Left | 左移動 | ← | プレイ中のみ有効 |
| Right | 右移動 | → | プレイ中のみ有効 |
| Down | ソフトドロップ | ↓ | プレイ中のみ有効 |
| A | 時計回り回転 | X | プレイ中 / 一部画面の確定補助 |
| B | 反時計回り回転 / 戻る | Z | プレイ中は回転、一部画面では戻る補助。PC では ESC を B の別名として扱ってよい |
| START | 開始 / 一時停止 / 再開 | Enter | 画面状態により意味が変わる |
| SELECT | 予約入力 | Right Shift | 初期実装では進行へ影響させない |

## 4. 受付方針
- プレイ中は Left / Right / Down / A / B / START を受け付ける
- SELECT は初期実装ではゲーム進行に影響させない
- ESC は新しい論理入力ではなく、PC 実装上の B の別名として扱ってよい
- Hard drop 相当の専用入力は定義しない
- 180 度回転入力は定義しない

## 5. 状態別入力マトリクス
| 状態 | 有効入力 | 無効入力 | 備考 |
|---|---|---|---|
| タイトル | START | Left, Right, Down, A, B, SELECT | START で開始設定へ進む |
| 開始設定 | Left, Right, A, B, START | Down | A / START は開始確定、B は戻る |
| プレイ中 | Left, Right, Down, A, B, START | 予約扱いの SELECT | START は一時停止 |
| 一時停止 | START, B（PC では ESC 可） | Left, Right, Down, A, SELECT | START で再開、B でタイトル復帰 |
| ゲームオーバー | START, A, B（PC では ESC 可） | Left, Right, Down, SELECT | START / A で再試行、B でタイトルへ戻る |

## 6. 同時入力と優先順
複数入力が同一更新単位で観測された場合、優先順は以下の通りとする。

1. START
2. 回転（A / B）
3. 左右移動（Left / Right）
4. Down
5. SELECT

補足:
- START は状態遷移入力であるため最優先とする
- Left と Right が同時に押された場合は相殺し、左右移動なしとして扱ってよい
- A と B が同時に押された場合は、両方無効としてよい

## 7. 押下継続の扱い
- 基本仕様では、押下継続時のリピート挙動は `36_input_timing_design.md` へ委譲する
- ただし外部仕様として、押しっぱなしで不規則な多重入力が発生してはならない
- START は押しっぱなしで連続トグルしてはならない

## 8. 非採用入力
- Hold
- Hard drop
- 180 度回転
- ポーズ中のピース操作

## 9. 表示文言方針
ユーザー向け説明では以下のいずれかで表記してよい。
- 論理入力名: `A`, `B`, `START`
- PC キー名: `X`, `Z`, `Enter`
- 併記: `A (X)` の形式

## 10. 受入観点
- 論理入力と PC 入力の対応が明確であること
- SELECT の扱いが曖昧でないこと
- Hard drop 非採用が確認できること
- 状態ごとの入力有効範囲が確認できること
- 同時入力の解釈が最低限定義されていること
