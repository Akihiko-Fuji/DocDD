# スコープ定義 / Scope Definition

- 文書ID: DOC-REQ-011
- 文書名: スコープ定義 / Scope Definition
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 本プロジェクトで対象とする範囲、対象外とする範囲、優先度、および参照仕様の境界を明確化する
- 関連文書:
  - `docs/00_overview/00_document_map.md`
  - `docs/00_overview/01_project_charter.md`
  - `docs/00_overview/04_reference_baseline_and_deltas.md`
  - `docs/01_requirements/13_functional_requirements.md`
  - `docs/01_requirements/14_non_functional_requirements.md`
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/04_quality_assurance/40_test_strategy.md`

---

## 1. 本書の目的

本書は、落下ブロックゲームを題材とした DocDD 見本プロジェクトについて、**何を対象とし、何を対象外とするか** を定義する文書である。

ゲーム題材は機能拡張候補が多く、参照元の Game Boy 版仕様も隠し要素を含む。そのため本書では、**実装対象** と **参照保持対象** と **明示的非採用** を分けて管理する。

---

## 2. スコープ定義の基本方針

1. DocDD の見本として説明しやすいことを最優先とする
2. 参照元は Game Boy 版テトリスとするが、完全再現ではなく説明可能な整理仕様として扱う
3. 初期開発の主軸は 1 人用 A-TYPE とする
4. B-TYPE は参照仕様として記述し、将来実装余地を残す
5. SELECT による NEXT 表示切替は Game Boy 基準として仕様へ含める
6. 10×18 盤面、NEXT 1 個、Hold なし、Hard drop なしを固定条件とする
7. T-Spin は本プロジェクト独自拡張として採用する
8. 2 人対戦、ハートレベル、リセットコマンド等の隠し/周辺要素は明示的に扱いを決める

---

## 3. スコープ分類

本プロジェクトのスコープは以下の 3 段階で扱う。

### 3.1 実装対象（Must Implement）

- タイトルから A-TYPE を開始できること
- 開始レベル 0〜9 を設定できること
- ピース落下、移動、回転、固定、ライン消去が成立すること
- SCORE / LINES / LEVEL / NEXT を表示できること
- SELECT で NEXT 表示を ON/OFF できること
- スコア、レベル進行、ゲームオーバー、一時停止が成立すること
- T-Spin を独自拡張として判定・得点反映できること

### 3.2 参照保持対象（Documented Baseline）

- B-TYPE の 25 lines、HIGH 0〜5
- Game Boy 系速度表、ソフトドロップ、ARE 等の数値基準
- 2 人対戦モードの存在そのもの
- ハートレベルの存在
- リセットコマンドの存在

これらは文書上は記載するが、初期実装の必須条件には含めない。

### 3.3 明示的対象外（Out of Scope）

- 対戦モード実装
- 通信プレイ
- Hold
- Hard drop
- Ghost 表示
- 180 度回転
- Combo / Back-to-Back / Perfect Clear ボーナス
- modern guideline 系 7-bag
- 高度な演出、ランキング、クラウド保存

---

## 4. 対象範囲（In Scope）

### 4.1 コアゲームプレイ

- 新規ゲーム開始
- A-TYPE 開始レベル選択（0〜9）
- 7 種テトロミノ出現
- 左右移動、A/B 回転、ソフトドロップ
- SELECT による NEXT 表示切替
- 接地判定、固定、ライン消去、詰め処理
- スコア計算、ライン数管理、A-TYPE レベル進行
- 一時停止、再開、ゲームオーバー、再試行
- T-Spin 判定および T-Spin 得点

### 4.2 外部仕様整備

- ゲームルール全体
- 画面構成と画面遷移
- 入力操作と状態別有効範囲
- 得点、レベル、速度表
- 回転と衝突判定
- ポーズ、再開、ゲームオーバー

### 4.3 内部設計整備

- 状態遷移の整理
- ルール処理順序の固定
- 入力処理、ゲーム進行、描画責務の分離
- NEXT 表示フラグを含む UI 状態の整理
- T-Spin 判定を含むルール責務の配置

### 4.4 品質保証対象

- 主要正常系の検証方針整理
- 壁際、床際、積み上がり等の境界条件試験
- SELECT による NEXT 表示切替試験
- T-Spin 判定の妥当性確認
- 文書とテストのトレーサビリティ確認

---

## 5. 対象外範囲（Out of Scope）

### 5.1 モード拡張

- 2 人対戦実装
- 通信プレイ
- ストーリー、ミッション、チャレンジ等の派生モード
- B-TYPE の初期実装

### 5.2 非採用ルール

- Hold
- Hard drop
- ゴースト表示
- Combo
- Back-to-Back
- Perfect Clear ボーナス
- wall kick / floor kick
- T-Spin Mini 区別

### 5.3 周辺機能

- 高度なリプレイ解析 UI
- オンラインランキング
- クラウドセーブ
- モバイル最適化
- ブラウザ配布前提調整

---

## 6. Game Boy 版との境界定義

### 6.1 準拠する項目

- A-TYPE / B-TYPE の基本モード定義
- 10×18 盤面
- NEXT 1 個
- SELECT で NEXT 表示切替
- A/B 回転、Hard drop なし
- スコア倍率とレベル進行
- HIGH 0〜5 を伴う B-TYPE 参照仕様

### 6.2 参照するが初期実装しない項目

- B-TYPE プレイフロー
- 2 人対戦
- ハートレベル
- リセットコマンド

### 6.3 独自拡張項目

- T-Spin と T-Spin 得点
- DocDD 用の受入観点、トレーサビリティ、レビュー記録
- PC キー写像

---

## 7. フェーズ整理

### 7.1 フェーズ1: DocDD 骨格成立

- コア 10 文書の整備
- 入力、得点、ポーズ周辺仕様の整備
- Game Boy ベースラインとの差分明示

### 7.2 フェーズ2: 基本プレイ成立

- A-TYPE のプレイ可能実装
- NEXT 表示切替を含む基本 UI
- T-Spin を含む主要ルールの実装

### 7.3 フェーズ3: 参照仕様拡張

- B-TYPE 参照仕様の詳細化または実装
- replay / config の実装対象化検討
- 2 人対戦やハートレベルの扱い再評価

---

## 8. 本書レベルの受入観点

1. 実装対象 / 参照保持対象 / 明示的対象外が分離されていること
2. A-TYPE 主軸、B-TYPE 参照という境界が明確であること
3. SELECT による NEXT 表示切替がスコープへ含まれていること
4. Hold なし、Hard drop なし、10×18、NEXT 1 個が固定条件として記載されていること
5. T-Spin が独自拡張として明示されていること

---

## 9. 変更履歴

- 2026-03-23: Game Boy 版の SELECT/NEXT、B-TYPE/HIGH、隠し要素の扱いをスコープ分類へ反映
- 2026-03-23: A-TYPE 主軸、B-TYPE 参照、T-Spin 拡張を明確化
