# 入力タイミング設計 / Input Timing Design

- 文書ID: DOC-DSN-036
- 最終更新日: 2026-03-23
- 関連文書:
  - `22_input_operation_spec.md`
  - `32_state_machine_design.md`
  - `adr/ADR-0001-game-loop-model.md`
  - `adr/ADR-0003-input-buffer-policy.md`

## 1. 目的
入力受付とゲーム更新の関係を整理し、回転・移動・一時停止の解釈順序を明確化する。

## 2. 基本順序
1. 入力スナップショット取得
2. 状態依存で有効入力を抽出
3. `START` を最優先で評価し、成立時は状態遷移のみを反映する
4. 回転（A / B）を評価する
5. 左右移動（Left / Right）を評価する
6. Down を評価する
7. 自動落下を評価する
8. 接地 / 固定判定へ渡す

## 3. 同時入力規則
- `START + 他入力`: `START` のみ反映する
- `Left + Right`: 相殺して左右移動なしとする
- `A + B`: 両方無効とする
- `Down + 左右移動/回転`: 優先順は本書 2 章に従う

## 4. T-Spin との関係
最終成立操作が回転かどうかを保持できるよう、成立した入力結果を frame 単位で記録する。

## 5. pause / resume バッファ方針
- 一時停止直前のプレイ操作は ST-PAUSE へ持ち越さない
- 再開直後は、同一押下継続による再度の pause を起こさないよう `START` を 1 frame 再評価しない

## 6. Diagram-Driven 観点
本書は `32_state_machine_design.md` のプレイフレーム順と同一の順序で読めなければならない。Mermaid 図や状態表を更新する場合は、本書の順序も同時に更新する。
