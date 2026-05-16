# ドメインモデル / Domain Model

- 文書ID: DOC-DSN-031
- 最終更新日: 2026-03-24
- 関連文書:
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/33_data_model.md`
  - `docs/03_internal_design/39_interface_contract.md`

## 1. 目的
本書は、仕様と実装の橋渡しとして、ランタイムで登場する主要概念の**意味、関係、多重度、集約境界、ライフサイクル**を定義する。`33_data_model.md` が型や不変条件の正本であるのに対し、本書は「なぜその概念が存在し、どの概念とどの粒度で結び付くか」を扱う。

## 2. モデリング原則

1. `GameSession` を 1 プレイ単位の集約根とする
2. 盤面、現在ピース、NEXT、得点は session 配下の整合した状態として扱う
3. 入力は永続状態ではなくフレーム単位の観測値として扱う
4. T-Spin やライン消去数のような判定結果は、長期保持データではなく処理段階で生成される派生概念として扱う
5. 一時停止は独立集約ではなく `GameSession.state` と `pause_reason` で表す

## 3. 主要概念一覧

| 概念 | 種別 | 説明 | ライフサイクル |
|---|---|---|---|
| `GameSession` | 集約根 | 1 回のプレイを束ねる実行時集約 | 開始時生成、終了時破棄 |
| `Board` | エンティティ相当 | 10×18 の可視盤面。固定済みセルの正本 | session 生成時初期化、毎フレーム更新 |
| `CurrentPiece` | エンティティ相当 | 現在操作中のピース状態 | spawn で生成、lock または game over で消滅 |
| `NextQueue` | 値オブジェクト / 小集約 | 外部仕様上は NEXT 1 個、内部では供給責務を含む | session 生成時初期化、spawn ごとに更新 |
| `ScoreState` | 値オブジェクト | SCORE / LINES / LEVEL の組 | session 中保持、score event ごとに更新 |
| `InputSnapshot` | 一時値 | フレーム単位の論理入力集合 | 毎フレーム生成、そのフレームで消費 |
| `TSpinResult` | 派生結果 | 固定後評価で得られる T-Spin 判定結果 | lock 後に生成、score 適用後は不要 |
| `PauseState` | 独立概念ではなく派生表現 | 一時停止中かどうかの UI / 遷移上の見え方 | `GameSession.state == ST-PAUSE` で表現 |
| `Config` | 起動時設定 | 開始レベル、入力デバイス、ボタン割当など | 起動時読込、セッション生成時参照 |
| `ReplayFrame` | 外部交換データ | replay の 1 レコード | 記録/再生時のみ存在 |

## 4. 概念間の関係

### 4.1 集約関係

| 親概念 | 子概念 | 多重度 | 関係種別 | 備考 |
|---|---|---|---|---|
| `GameSession` | `Board` | 1..1 | 合成 | board は session なしで存在しない |
| `GameSession` | `CurrentPiece` | 0..1 | 合成 | pause 中も保持しうる。game over 確定後は `None` 可 |
| `GameSession` | `NextQueue` | 1..1 | 合成 | visible NEXT は常に 1 個必要 |
| `GameSession` | `ScoreState` | 1..1 | 合成 | score/lines/level は常に一体で更新 |
| `GameSession` | `InputSnapshot` | 0..1 | 一時参照 | そのフレーム評価中だけ保持してよい |
| `GameSession` | `Config` | 1..1 参照 | 参照 | session 生成時に start level 等を取り込む |
| `CurrentPiece` | `TSpinResult` | 0..1 | 派生 | 固定後評価時のみ生成 |

### 4.2 主要関係の意味

- `GameSession` と `Board` は **1 対 1** であり、複数盤面や共有盤面は持たない
- `GameSession` と `CurrentPiece` は通常プレイ中は **1 対 1** だが、タイトル・設定・ゲームオーバーでは **0 対 1** となる
- `NextQueue` は名称上 queue を許容しても、外部仕様上の表示多重度は **常に 1** である
- `InputSnapshot` は session の長期状態ではなく、**フレーム評価用の短命オブジェクト**である

## 5. 集約境界と整合性ルール

### 5.1 `GameSession` 集約の境界

`GameSession` 集約に含めるもの:

- 上位状態 `ST-*` とプレイサブ状態 `PL-*`
- `Board`
- `CurrentPiece`
- `NextQueue`
- `ScoreState`
- フレーム番号
- pause reason
- randomizer seed

`GameSession` 集約に含めないもの:

- 物理入力デバイス状態そのもの
- 画面レイアウト計算結果
- replay ファイル I/O 状態
- T-Spin / ライン消去の一時的な計算途中値

### 5.2 集約内の整合性制約

1. `state == ST-PLAY` の間は `Board`, `NextQueue`, `ScoreState` が必須である
2. `play_substate == PL-ACTIVE` の間は `CurrentPiece` が必須である
3. `state != ST-PLAY` のとき、`CurrentPiece` は保持してもよいが更新してはならない
4. `ScoreState` の `lines` と `level` は同一 score event の中で整合した順序で更新される必要がある
5. `Board` 更新は current piece の固定結果を反映した後にのみ行い、renderer が board を直接変更してはならない

## 6. ライフサイクル定義

### 6.1 `GameSession`

1. タイトルまたは設定画面で開始確定される
2. 既定値または `Config` に基づいて生成される
3. プレイ中はフレームごとに更新される
4. game over またはタイトル復帰で破棄対象になる
5. 再試行では旧 session を再利用せず、新規 session を生成する

### 6.2 `Board`

1. session 生成時に空盤面で初期化される
2. current piece の固定時のみ占有セルが増える
3. ライン消去で行再構成される
4. session 終了とともに破棄される

### 6.3 `CurrentPiece`

1. `spawn_service` により生成される
2. `PL-ACTIVE` 中に移動・回転・落下で更新される
3. 下移動不能後、lock によって board へ反映される
4. lock 完了時に消滅し、次の spawn まで存在しない

### 6.4 `InputSnapshot`

1. フレーム先頭で生入力または replay から生成される
2. `state_controller` が有効入力を評価する
3. 必要に応じて gameplay services へ伝搬される
4. そのフレーム終了時には参照不要となる

### 6.5 `TSpinResult`

1. lock 後に T ピース固定である可能性がある場合のみ評価対象になる
2. `tspin_detector` が生成する
3. `scoring_service` が消費した後は保存不要である

## 7. ドメイン上の制約

### 7.1 盤面とピース
- `Board` は可視 10×18 を超える固定済みセルを保持しない
- `CurrentPiece` は常に 4 セルからなる 1 つのテトロミノとして扱う
- 回転失敗は `CurrentPiece` の同一性を保ったまま、向き変更なしとして扱う

### 7.2 得点と判定
- `ScoreState` は score/lines/level を分離保存しても、更新イベントは 1 つのまとまりとして扱う
- `TSpinResult` は得点値そのものを持たず、判定結果だけを表す
- T-Spin 不成立時でも `TSpinResult` 相当の「不成立」結果を返してよい

### 7.3 一時停止
- `PauseState` を別エンティティとして持たず、`GameSession.state` に吸収する
- pause 中は `Board`, `CurrentPiece`, `ScoreState` が凍結され、表示用に参照だけ許可される

## 8. 実装判断のための補足

- `GameSession` と `Board` の関係は「持つ」ではなく **合成 1..1** であるため、board 単体差し替えを常用する設計は避ける
- `CurrentPiece` は session の一部だが短命なので、履歴保存が必要なら snapshot や replay で別に扱う
- `InputSnapshot` を永続状態として持ち続けると責務が混線するため、フレーム境界を越えて保持しない
- `PauseState` を独立概念にしないことで、状態遷移の正本を `32_state_machine_design.md` に一本化できる

## 9. DocDD 追跡で特に重要な概念

- `GameSession`: 状態遷移、スコア、盤面を束ねる集約根
- `InputSnapshot`: UI / 入力仕様から内部契約へ接続する橋渡し概念
- `TSpinResult`: 外部仕様の T-Spin 条件を得点処理へ接続する派生概念
- `ScoreState`: A-TYPE の LINES / LEVEL / SCORE を一体で保持する値オブジェクト
