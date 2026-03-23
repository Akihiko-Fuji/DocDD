# 入力操作仕様 / Input Operation Specification

- 文書ID: DOC-SPC-022
- 文書名: 入力操作仕様 / Input Operation Specification
- 最終更新日: 2026-03-24
- 関連文書:
  - `20_game_rules_spec.md`
  - `21_ui_screen_spec.md`
  - `24_piece_rotation_collision_spec.md`
  - `25_pause_gameover_resume_spec.md`
  - `32_state_machine_design.md`
  - `36_input_timing_design.md`
  - `adr/ADR-0003-input-buffer-policy.md`

## 1. 目的
Game Boy 版基準の論理入力を PC 実装へ写像し、状態別の有効入力、優先順、競合解釈を定義する。

## 2. 基本方針
1. ユーザー向け説明では Game Boy 系の論理ボタン名を保持する
2. 実装では HID キーボードまたはゲームパッドの物理入力へ対応付ける
3. 入力は状態依存で有効 / 無効を切り替える
4. Hard drop や Hold など、採用しない入力は明示的に不採用とする
5. 同一更新単位で競合する入力は本書の優先順で解釈する
6. `START` は状態遷移入力として通常プレイ操作より優先する
7. `SELECT` はプレイ中のみ NEXT 表示切替に用いる
8. 物理入力差異は `config.ini` の設定で吸収する

## 3. 論理入力
| 論理入力 | 役割 | キーボード推奨割当例 | ゲームパッド割当例 | 備考 |
|---|---|---|---|---|
| Left | 左移動 | ArrowLeft | D-Pad Left | プレイ中のみ有効 |
| Right | 右移動 | ArrowRight | D-Pad Right | プレイ中のみ有効 |
| Down | ソフトドロップ | ArrowDown | D-Pad Down | プレイ中のみ有効 |
| A | 時計回り回転 | KeyX | Button 1 / South | プレイ中 / 一部画面の確定補助 |
| B | 反時計回り回転 / 戻る | KeyZ / Escape | Button 2 / West | プレイ中は回転、一部画面では戻る補助 |
| START | 開始 / 一時停止 / 再開 | Enter | Start | 画面状態により意味が変わる |
| SELECT | NEXT 表示 ON/OFF 切替 | ShiftRight | Select / Back | プレイ中のみ有効 |

補足:
- `Up` は本プロジェクトでは独立した論理入力として定義しない
- 開始設定画面のレベル変更は `Left / Right` で統一する
- `P` は論理入力を増やさず、実装上の別名にも採用しない
- 物理入力の最終割当は `config.ini` の `input_interface` とボタン定義を参照する

## 4. 入力インターフェース方針
- 主入力インターフェースは HID キーボード（標準入力）とする
- ゲームパッド対応を許可し、十字キー相当と `A/B/START/SELECT` 相当ボタンへ写像する
- どのインターフェースを利用するかは `config.ini` の `input_interface` で選択する
- 物理キー/ボタン割当は `config.ini` で定義し、本書では論理入力名を正本とする

## 5. 受付方針
- プレイ中は `Left / Right / Down / A / B / START / SELECT` を受け付ける
- SELECT はプレイ中のみ NEXT 表示の切替へ使用する
- ESC は新しい論理入力ではなく、キーボード運用時の B の別名として扱ってよい
- Hard drop 相当の専用入力は定義しない
- 180 度回転入力は定義しない

## 6. 状態別入力マトリクス
| 状態 | 有効入力 | 無効入力 | 備考 |
|---|---|---|---|
| タイトル | START | Left, Right, Down, A, B, SELECT | START で開始設定へ進む |
| 開始設定 | Left, Right, A, B, START | Down, SELECT | Left / Right でレベル変更、A / START は開始確定、B は戻る |
| プレイ中 | Left, Right, Down, A, B, START, SELECT | - | START は一時停止、SELECT は NEXT 切替 |
| 一時停止 | START, B（PC では ESC 可） | Left, Right, Down, A, SELECT | START で再開、B でタイトル復帰 |
| ゲームオーバー | START, A, B（PC では ESC 可） | Left, Right, Down, SELECT | START / A で再試行、B でタイトルへ戻る |

## 7. 同時入力と優先順
複数入力が同一更新単位で観測された場合、優先順は以下の通りとする。

1. START
2. SELECT
3. 回転（A / B）
4. 左右移動（Left / Right）
5. Down

補足:
- START は状態遷移入力であるため最優先とする
- SELECT は UI 状態のみを切り替え、ピース座標やキューを変更しない
- Left と Right が同時に押された場合は相殺し、左右移動なしとして扱う
- A と B が同時に押された場合は、両方無効として扱う
- START と他のプレイ入力が同時に押された場合、プレイ入力は反映しない

## 8. 押下継続の扱い
- 基本仕様では、押下継続時のリピート挙動は `36_input_timing_design.md` へ委譲する
- 押しっぱなしで不規則な多重入力が発生してはならない
- START は押しっぱなしで連続トグルしてはならない
- SELECT は押しっぱなしで高速点滅のような不自然な連続切替を起こしてはならない
- 一時停止解除直後は、同一押下継続による再度の一時停止を起こしてはならない

## 9. 非採用入力
- Hold
- Hard drop
- 180 度回転
- ポーズ中のピース操作
- `Up` を使う別系統メニュー操作

## 10. `config.ini` 参照方針
- `config.ini` は少なくとも `[input]` セクションと、利用するインターフェースごとのボタン定義を持つ
- 例: `input_interface=keyboard` または `input_interface=gamepad`
- キーボード時は `left=ArrowLeft` のようなキーコード、ゲームパッド時は `a=Button1` のようなボタン名を保持する
- 実装は `config.ini` を読み取り、論理入力 `Left / Right / Down / A / B / START / SELECT` へ正規化する

## 11. 表示文言方針
ユーザー向け説明では以下のいずれかで表記してよい。
- 論理入力名: `A`, `B`, `START`, `SELECT`
- キーボード物理入力名: `X`, `Z`, `Enter`, `Right Shift`
- ゲームパッド物理入力名: `Button 1`, `Start`, `Select` など
- 併記: `SELECT (Right Shift)` や `A (Button 1)` の形式

## 12. 受入観点
- 論理入力と PC 入力の対応が明確であること
- 開始設定画面で `Left / Right` 以外をレベル変更へ使わないこと
- SELECT の扱いが曖昧でないこと
- プレイ中に SELECT で NEXT 表示切替ができること
- Hard drop 非採用が確認できること
- 状態ごとの入力有効範囲が確認できること
- 同時入力の解釈と START 優先が定義されていること


## 13. 変更履歴
- 2026-03-24: HID キーボード主入力、ゲームパッド対応、`config.ini` による入力インターフェース切替を追加
