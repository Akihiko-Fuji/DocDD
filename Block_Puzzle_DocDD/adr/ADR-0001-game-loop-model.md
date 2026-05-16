# ADR-0001: ゲームループ方式 / Game Loop Model

- ADR-ID: ADR-0001
- 最終更新日: 2026-03-23
- 状態: Accepted
- 目的: Game Boy 版基準の落下挙動を保ちつつ、DocDD 上で仕様・設計・試験へ追跡しやすいゲームループ方式を固定する
- 関連文書:
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/36_input_timing_design.md`

## 1. 決定
ゲームループは **固定更新幅（frame-based fixed step）** を採用する。

1. 1 更新単位を 1 frame として扱う
2. 入力は毎 frame 冒頭でスナップショット化する
3. `START` は状態遷移入力として最優先で評価する
4. プレイ中は `回転 -> 左右移動 -> Down -> 自動落下` の順で評価する
5. 固定後は `ライン判定 -> ライン消去 -> T-Spin 判定 -> 得点 -> ライン数 -> レベル -> 次ピース準備 -> 終了判定` の順で処理する

## 2. 理由
- Game Boy 版由来のフレーム基準落下速度表と整合しやすい
- 入力優先順を仕様・設計・テストへ一貫して落とし込みやすい
- DocDD 上で TC へ直接接続しやすい

## 3. 代替案
### 3.1 可変 delta time
却下。入力優先順や落下速度表の説明が複雑になり、Game Boy 基準との対応も弱くなるため。

### 3.2 イベント駆動中心ループ
却下。文書上の状態遷移は表現できるが、入力競合時の評価順を読み取りにくくなるため。

## 4. 影響
- `32_state_machine_design.md` のプレイフレーム順序をこの ADR に従って固定する
- `36_input_timing_design.md` はこの ADR を正本として整合させる
- `44_performance_test_plan.md` は frame 安定性と入力反映 frame を評価する

## 5. 未採用事項
- lock delay の追加
- wall kick / floor kick
- 可変時間補間による高リフレッシュレート最適化

## 6. 変更履歴
- 2026-03-23: 固定更新幅と入力優先順を採用決定
