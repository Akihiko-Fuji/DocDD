# 入力タイミング設計 / Input Timing Design

- 文書ID: DOC-DSN-036
- 最終更新日: 2026-03-24
- 関連文書:
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/03_internal_design/30_architecture_design.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/39_interface_contract.md`
  - `adr/ADR-0001-game-loop-model.md`
  - `adr/ADR-0003-input-buffer-policy.md`

## 1. 目的
入力受付と fixed-step ゲーム更新の関係を整理し、回転・移動・pause・自動落下が**どの tick のどの順序で解釈されるか**を明確化する。`32_state_machine_design.md` が状態遷移責務を定義するのに対し、本書はフレーム時間軸上の処理順とバッファ規則を定義する。

## 2. 前提

- ゲームループモデルは `ADR-0001-game-loop-model.md` の fixed-step 方針に従う
- 1 tick で評価する入力の正本は `InputSnapshot` とする
- `InputSnapshot` は tick 先頭で 1 回だけ生成し、その tick 中は不変とする
- replay 再生時も通常入力と同じ `InputSnapshot` 経路へ流す

## 2.1 タイムステップ定義

- 論理フレームレートは **60 fps** とする
- 1 フレームの実時間目標は **16.67 ms** とする
- `20_game_rules_spec.md` や `23_scoring_level_spec.md` の速度表で用いるフレーム数は、この 60 fps を前提とする
- ゲーム内の論理時間は実時間ではなく **経過フレーム数** を正本とする

## 2.2 遅延時の方針

- 処理遅延が発生した場合でも、実時間へ追いつくために論理フレームをまとめて進めない
- すなわち本プロジェクトでは catch-up 更新を採らず、**遅延許容** とする
- ゲームの論理時間は「何フレーム経過したか」のみで管理し、壁時計時間との差は補正対象にしない
- 1 フレーム目標である 16.67 ms を超える tick が発生した場合は、ログ出力できる構造にする
- 遅延による一時的な体感差異は、テスト上の再現対象外とする

## 3. 1 tick の標準処理順

```text
tick start
  1. raw input / replay record 取得
  2. InputSnapshot 生成
  3. 状態依存で有効入力を抽出
  4. START 評価
  5. SELECT 評価
  6. 回転評価
  7. 左右移動評価
  8. Down 評価
  9. 自動落下タイマ評価
 10. 接地 / 固定判定
 11. 固定後処理（消去 / T-Spin / 得点 / 次ピース）
 12. 描画用 snapshot 構築
tick end
```

## 4. 優先順と解釈規則

### 4.1 基本優先順
1. `START`
2. `SELECT`
3. 回転（A / B）
4. 左右移動（Left / Right）
5. `Down`
6. 自動落下

### 4.2 優先順の理由
- `START` は状態遷移入力であり、同 tick の盤面更新より優先する必要がある
- `SELECT` は進行を変えない UI 切替であり、pause より下・回転より上に置く
- 回転を左右移動より先にすることで、T-Spin 判定に必要な「最終成立操作」の意味が安定する
- `Down` を自動落下より先にすることで、プレイヤー入力を機械的落下より優先する

## 5. 同時入力規則

| 同時入力 | 解釈 |
|---|---|
| `START + 他入力` | `START` のみ反映し、他入力は破棄 |
| `Left + Right` | 相殺して左右移動なし |
| `A + B` | 両方不成立として回転なし |
| `Down + Left/Right` | 回転・左右移動・Down の順で評価 |
| `Down + A/B` | 回転成立後に Down を評価 |
| `SELECT + 他プレイ入力` | `SELECT` は UI 状態のみを更新し、他のプレイ入力評価は継続 |

## 6. 自動落下タイマ管理

### 6.1 管理単位
- 自動落下タイマは `CurrentPiece` 単位または session 内の active piece 文脈で管理する
- ピース出現時にタイマを初期化する
- fixed-step ごとに経過 tick を加算し、重力閾値到達時に 1 マス落下を試みる

### 6.2 リセット条件
- 新しい current piece が出現したとき
- pause から再開し、再開 tick を新しい評価境界として扱うとき
- ピース固定後に次ピースへ切り替わったとき

### 6.3 凍結条件
- `ST-PAUSE` 中は自動落下タイマを進めない
- `ST-TITLE`, `ST-SETUP-A`, `ST-GAMEOVER` ではタイマを持たない

## 7. 固定・後処理との接続

- Down と自動落下のいずれでも下移動不能が観測された場合、同 tick 内で `PL-LOCK-CHECK` へ進めてよい
- lock 成立後は同 tick 内でライン消去、T-Spin 判定、得点更新、レベル更新、次ピース準備まで完了させる
- その結果、次 tick 開始時には新しい current piece または `ST-GAMEOVER` のいずれかになっていることを期待する

## 8. pause / resume バッファ方針

### 8.1 pause 進入時
- 一時停止直前 tick のプレイ操作は、pause 中へ持ち越さない
- `START` が成立した tick では、回転・左右移動・Down・自動落下を評価しない

### 8.2 resume 時
- 再開直後は同一押下継続による再 pause を避けるため、`START` の再評価を 1 tick 抑止する
- この抑止は `START` のみに適用し、他プレイ入力の初回受付を不当に遅延させない

### 8.3 replay 再生時
- replay でも `START` の pause/resume 規則は通常入力と同一に扱う
- したがって replay の再現条件には本書のバッファ規則が含まれる

## 9. T-Spin 判定との関係

- T-Spin 判定には「最終成立操作が回転であること」が必要である
- そのため回転失敗時は `last_successful_action` を回転へ更新してはならない
- 回転成立後に Down や自動落下が起きても、lock までの間は最後に成立した操作を保持する

## 10. 図と他文書との関係

- `32_state_machine_design.md` の「プレイフレーム内の処理順」は本書の要約版として一致していなければならない
- `39_interface_contract.md` では `InputSnapshot` と `TransitionResult` の前後条件を扱う
- タイムライン全体のレビューでは、本書を fixed-step の時間軸正本として扱う
- 速度表のフレーム数を変更する場合は、本書の 60 fps 前提と同時に更新する

## 11. 受入観点

- 同時入力時の解釈がテストケースへ落とせる粒度で書かれていること
- pause/resume で入力バッファと自動落下タイマの扱いが曖昧でないこと
- replay 再生時も通常入力と同一の時間規則で処理されること
- `32_state_machine_design.md` と順序矛盾がないこと
