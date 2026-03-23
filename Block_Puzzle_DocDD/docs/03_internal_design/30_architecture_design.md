# アーキテクチャ設計 / Architecture Design

- 文書ID: DOC-DSN-030
- 最終更新日: 2026-03-24
- 関連文書:
  - `27_runtime_flowchart_mermaid.md`
  - `31_domain_model.md`
  - `32_state_machine_design.md`
  - `33_data_model.md`
  - `34_module_design.md`
  - `35_rendering_design.md`
  - `36_input_timing_design.md`
  - `37_error_handling_policy.md`
  - `39_interface_contract.md`
  - `adr/ADR-0001-game-loop-model.md`

## 1. 目的
外部仕様を実装へ落とすための**上位アーキテクチャ境界とデータ流れ**を定義し、責務混在を防ぐ。`34_module_design.md` が各モジュール契約の設計書であるのに対し、本書は「なぜその分割にするか」「各層をどの方向へ依存させるか」を扱う。

## 2. 本書が扱う範囲

- 層ごとの責務境界と依存方向
- フレーム更新における入力、状態遷移、ルール処理、描画の受け渡し順
- `InputSnapshot`, `GameSession`, `ScreenViewModel` など主要データの生成地点と所有者
- 将来拡張である persistence をどの境界へ接続するか

以下は本書では正本化しない。

- 個別モジュールの関数契約: `34_module_design.md`, `39_interface_contract.md`
- 具体的なレイアウト値や UI 表示条件: `35_rendering_design.md`
- 入力評価の詳細優先順: `36_input_timing_design.md`

## 3. アーキテクチャの設計原則

1. **外部入力と内部ルールを分離する。** 物理デバイス差異は `input_mapper` より上で閉じ込める。
2. **状態遷移とルール適用を分離する。** どの入力が有効かを決める責務と、盤面へどう作用するかを決める責務を同一層へ混在させない。
3. **GameSession を唯一のランタイム集約とする。** ただし集約が巨大化しないよう、判定ロジックはサービスへ委譲する。
4. **描画は read-only な下流層とする。** renderer は `GameSession` を変更してはならない。
5. **予約機能は境界だけ先に固定する。** persistence は現行 build で未実装でも、接続点だけは設計しておく。

## 4. 層構成

```text
Physical Input / Replay Source
  -> Input Normalization Layer
  -> State Coordination Layer
  -> Gameplay Application Layer
  -> Presentation Mapping Layer
  -> Screen Output / Log / Persistence Adapter(Reserved)
```

### 4.1 各層の責務

| 層 | 主責務 | 代表データ | この層でやらないこと |
|---|---|---|---|
| Physical Input / Replay Source | キーボード、ゲームパッド、replay などの生入力取得 | raw input event | 状態遷移、盤面更新 |
| Input Normalization Layer | 生入力を `InputSnapshot` へ正規化する | `InputSnapshot` | ゲームルール適用 |
| State Coordination Layer | 現状態で有効な入力判定、遷移先決定、フレーム進行の分岐 | `TransitionResult`, `GameSession.state` | 衝突判定、得点計算 |
| Gameplay Application Layer | ピース操作、固定、消去、得点、レベル更新、NEXT 供給 | `GameSession`, `RuleResult` | UI レイアウト生成 |
| Presentation Mapping Layer | セッション状態を描画用 view model に変換 | `ScreenViewModel` | 盤面更新、状態遷移 |
| Screen Output / Log / Persistence Adapter | view model の実描画、ログ出力、保存 I/O | draw command, log entry | ゲームルール決定 |

## 5. 依存方向ルール

### 5.1 一方向依存

- 上流層は下流層の抽象契約を呼び出してよい
- 下流層は上流層へ逆依存してはならない
- renderer は `GameSession` の参照だけを行い、`state_controller` や `board_rules` を直接呼ばない

### 5.2 許可される代表依存

- `input_mapper -> Config`
- `state_controller -> GameSession`, `InputSnapshot`, `TransitionPolicy`
- `active_piece_service / lock_resolver / scoring_service -> GameSession` またはその部分モデル
- `renderer -> SessionView / ScreenViewModel`

### 5.3 禁止依存

- `renderer -> board_rules`, `scoring_service`
- `input_mapper -> state_controller`
- `persistence adapter -> renderer` を経由した保存判定
- `GameSession` 自身に物理入力解釈や描画レイアウト計算を持たせること

## 6. 主要データ流れ

### 6.1 起動からプレイ開始まで

1. 起動時に `config.ini` を読込み、`Config` へ正規化する
2. タイトル画面では `InputSnapshot` を用いて開始導線のみ評価する
3. 開始確定時に `game_session.create_new_game(config)` を呼び、新規 `GameSession` を生成する
4. `spawn_service` が最初の current piece と visible NEXT を準備する
5. renderer は初期 `GameSession` から `ScreenViewModel` を構築してプレイ画面へ渡す

### 6.2 1 フレーム更新の標準フロー

```text
raw input / replay frame
  -> input_mapper が InputSnapshot を生成
  -> state_controller が有効入力と遷移要否を判定
  -> ST-PLAY の場合のみ gameplay services が RuleResult を生成
  -> game_session が RuleResult を反映
  -> renderer が ScreenViewModel を構築
  -> output adapter が描画 / ログ出力
```

### 6.3 `InputSnapshot` の生成地点と所有

- 生成地点は `input_mapper` または replay adapter とする
- `InputSnapshot.frame` は `GameSession.frame` と一致させる
- `state_controller` は `InputSnapshot` をそのフレームの入力正本として扱い、後段サービスへ必要最小限だけ伝搬する
- gameplay services は `InputSnapshot` を保存用長期状態として保持せず、そのフレーム処理が終われば破棄してよい

### 6.4 `GameSession` の更新責務

- `GameSession` は集約正本であり、board / current piece / score / state を保持する
- 更新は `state_controller` または gameplay services の結果を通じてのみ行う
- renderer は `GameSession` を変更しない

### 6.5 描画用 view model の生成地点

- `renderer.build_view_model(session)` が唯一の生成地点とする
- `ScreenViewModel` は 640×576 基準座標系上の矩形、ラベル、数値、オーバーレイ可否を持つ
- UI 実装は `ScreenViewModel` を画面 API へ投影するだけに留める

## 7. フレーム制御と ADR-0001 との関係

- ゲームループの大枠は `ADR-0001-game-loop-model.md` の fixed-step 方針に従う
- 本書では、その fixed-step の各 tick でどの層が何を担当するかを規定する
- 自動落下タイマ、pause/resume バッファ、入力優先順などの詳細タイミング規則は `36_input_timing_design.md` を正本とする

## 8. 予約 Persistence の接続境界

### 8.1 Config 読込
- 起動時 adapter が `config.ini` を読込み、`Config` へ正規化して application 側へ渡す
- 読込失敗時のフォールバック方針は `37_error_handling_policy.md` を正本とする

### 8.2 Replay 記録 / 再生
- replay 記録は `InputSnapshot` と `randomizer_seed` を下流 adapter が受け取って外部形式へ変換する
- replay 再生は外部 `ReplayFrame` を `InputSnapshot` へ変換して通常入力経路へ流す
- replay は state_controller より下流へ特別扱いの API を増やさず、通常入力経路へ合流させる

## 9. `34_module_design.md` との書き分け

- 本書: 層の責務境界、依存方向、データ流れ、設計理由
- `34_module_design.md`: 各モジュールの責務、入出力、依存、公開契約、試験観点
- `39_interface_contract.md`: モジュール間の引数型・戻り値・前後条件の一覧

実装レビューでは、まず本書で「どこへ責務を置くべきか」を確認し、次に `34_module_design.md` と `39_interface_contract.md` で具体契約を確認する。

## 10. 受入観点

- Input / State / Gameplay / Rendering / Persistence(予約) の境界が根拠つきで読めること
- `InputSnapshot` を誰が生成し、誰が消費し、どこで破棄できるかが明確であること
- `34_module_design.md` と重複ではなく補完関係になっていること
- fixed-step ベースのフレーム更新が `ADR-0001` と矛盾しないこと
