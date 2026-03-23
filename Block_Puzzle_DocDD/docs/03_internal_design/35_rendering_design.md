# 描画設計 / Rendering Design

- 文書ID: DOC-DSN-035
- 最終更新日: 2026-03-24
- 関連文書:
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/03_internal_design/30_architecture_design.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/03_internal_design/39_interface_contract.md`

## 1. 目的
UI 仕様で求める表示要素を、**添付の Game Boy 風参考画面を 640×480 に拡張した基準レイアウト**として、どの領域へ、どの優先度で、どの状態で表示するかを定義する。`34_module_design.md` が renderer の責務境界を扱うのに対し、本書は renderer が生成すべき view model の構造とレイアウト方針を扱う。

## 2. 描画設計の原則

1. 盤面視認性を最優先し、参考画像と同じく「広いプレイフィールド + 右側縦積み情報欄」の構図を維持する
2. 右側情報欄は **SCORE -> LEVEL -> LINES -> NEXT** の順に上から並べる
3. 参考画像の濃色サイドパネル、枠線、余白を踏襲し、盤面と情報欄の視覚的境界を明確にする
4. オーバーレイ表示は進行状態を覆い隠しても、盤面参照が不能にならないようにする
5. レイアウトは 640×480 を正本座標系とし、実画面側でスケーリングする
6. Hold、ghost、Hard drop など非採用 UI は view model に含めない

## 3. 基準レイアウト

### 3.1 参考画像を基にした画面分割

参考画像では、左側に大きなプレイフィールド、中央に縦の装飾境界、右側に濃色の情報欄があり、その内部へ `SCORE`, `LEVEL`, `LINES`, `NEXT` が上から順に配置されている。本書ではこの構図を 640×480 に拡張して正本化する。

```text
+------------------------------------------------------------------+
|                                                                  |
|  brick border   playfield                brick border  side info |
|  x:40-71        x:88-327                 x:344-375    x:392-591  |
|                                                                  |
|                                                     SCORE        |
|                                                     LEVEL        |
|                                                     LINES        |
|                                                     NEXT         |
|                                                                  |
+------------------------------------------------------------------+
```

### 3.2 主要領域の矩形

| 領域 | x | y | w | h | 用途 |
|---|---:|---:|---:|---:|---|
| `playfield_left_border` | 40 | 24 | 32 | 400 | 左装飾境界 |
| `playfield_frame` | 88 | 24 | 240 | 400 | 10×18 盤面の外枠と背景 |
| `playfield_cells` | 104 | 64 | 160 | 288 | セル描画領域 |
| `playfield_right_border` | 344 | 24 | 32 | 400 | 右装飾境界 |
| `side_panel_background` | 392 | 24 | 200 | 400 | 濃色の情報欄背景 |
| `score_panel` | 424 | 40 | 144 | 72 | SCORE 表示 |
| `level_panel` | 424 | 136 | 144 | 72 | LEVEL 表示 |
| `lines_panel` | 424 | 232 | 144 | 72 | LINES 表示 |
| `next_panel` | 424 | 328 | 144 | 88 | NEXT 表示 |
| `status_message_anchor` | 208 | 20 | 224 | 24 | T-Spin / pause / game over の短文表示 |

補足:
- `playfield_cells` は 1 セル 16×16 の整数グリッドを前提とし、10×18 を収める
- 参考画像では盤面が外枠内でやや下寄りに見えるため、盤面セル領域はフレーム上端から 40px の余白を取る
- 情報欄は独立した濃色背景上に、同系統の枠付きパネルを縦積みする

## 4. 状態ごとの表示責務

### 4.1 タイトル (`ST-TITLE`)
- タイトル名
- START 導線
- 最低限の操作案内
- 盤面、NEXT、SCORE 等のプレイ用パネルは表示しない

### 4.2 開始設定 (`ST-SETUP-A`)
- 開始レベル値
- 変更方法の案内
- 開始確定 / 戻る導線

### 4.3 プレイ中 (`ST-PLAY`)
- 盤面
- current piece
- visible NEXT（表示フラグが有効な場合）
- SCORE / LEVEL / LINES を参考画像と同じ順序で表示
- 必要に応じて短時間メッセージ（例: T-Spin）

### 4.4 一時停止 (`ST-PAUSE`)
- 盤面の静止表示
- SCORE / LINES / LEVEL の固定表示
- 中央または `status_message_anchor` に `PAUSE` オーバーレイ
- 再開 / タイトル復帰導線

### 4.5 ゲームオーバー (`ST-GAMEOVER`)
- 最終盤面の静止表示
- 最終 SCORE / LINES / LEVEL
- `GAME OVER` 表示
- 再試行 / タイトル復帰導線

## 5. View Model 設計

### 5.1 renderer の入力
- `GameSession`
- UI 表示用の補助メッセージ
- NEXT 表示フラグ

### 5.2 renderer の出力

`ScreenViewModel` は少なくとも以下を含む。

| 要素 | 内容 |
|---|---|
| `screen_state` | title / setup / play / pause / gameover |
| `rects` | 領域矩形の一覧 |
| `board_cells` | 盤面セルの色・種別・座標 |
| `current_piece_cells` | 操作中ピースの描画セル |
| `labels` | `SCORE`, `LEVEL`, `LINES`, `NEXT`, 導線文言 |
| `numeric_values` | score/level/lines 数値 |
| `overlays` | pause / game over / T-Spin 表示 |

### 5.3 View Model に含めないもの
- 盤面衝突判定結果
- T-Spin 成立のロジックそのもの
- 自動落下タイマ値
- 物理入力デバイスの raw 状態

## 6. 640×480 上の具体レイアウト規則

### 6.1 盤面
- 可視 10×18 を固定表示し、セルサイズは 16px を基準とする
- 左上原点は `playfield_cells` の `(104, 102)` とする
- 1 セルごとの描画位置は `x = 104 + 16 * col`, `y = 102 + 16 * row` とする

### 6.2 NEXT パネル
- 参考画像に合わせ、NEXT は右側情報欄の最下段へ配置する
- NEXT 非表示フラグ時はパネル枠ごと非表示にし、上段の数値パネル位置は詰めずに空白として扱う
- version 1 では 1 個先のみを描画し、複数 preview を描画してはならない

### 6.3 数値パネル
- `SCORE`, `LEVEL`, `LINES` はこの順に縦積みで右側へ整列配置する
- 参考画像に合わせ、各パネルは同寸法・同余白の繰り返しパターンとする
- ラベルは上寄せ中央寄り、値は下段中央寄せを基本とし、Game Boy 風の「見出し + 数値」二段構成を維持する
- 数値更新はゲームロジックに追随するが、描画側で丸めや推定を行わない

### 6.4 メッセージ / オーバーレイ
- T-Spin メッセージは `status_message_anchor` 周辺に短時間表示する
- `PAUSE`, `GAME OVER` は盤面の視認を完全には妨げない半透明または明確な帯表示を想定する
- 長文メッセージは扱わず、短い固定句に留める

## 7. `34_module_design.md` との役割分担

- `34_module_design.md`: renderer が何を入力に取り、何を返すかという責務・契約
- 本書: renderer が返す view model に何を載せ、どこへ配置するか

したがって、本書では renderer 内部アルゴリズムや描画 API の選定には立ち入らない。

## 8. 素材形式と仕様

### 形式
- 全素材は PNG とする
- 透過が必要な素材（ブロックセル、装飾境界、オーバーレイ）は RGBA PNG
- 透過が不要な素材（背景、パネル）は RGB PNG

### 基準サイズ
- 1 セルの基準サイズは 16×16 px とする
- 全素材は整数倍スケールを前提として制作する

### ブロック素材
- ピース種別（I/O/T/J/L/S/Z）ごとに 1 素材とする
- 固定済みブロックと操作中ブロックは同一素材を使用する
  （Game Boy 版準拠のため、色・外観の変化は行わない）

## 9. 受入観点

- `21_ui_screen_spec.md` の必須表示要素と状態ごとの表示責務が一致すること
- 640×480 上で盤面、NEXT、SCORE、LINES、LEVEL が重ならずに配置できること
- 非採用 UI 要素が view model に混入していないこと
- renderer がルール判定を持たず、表示責務に限定されていること
