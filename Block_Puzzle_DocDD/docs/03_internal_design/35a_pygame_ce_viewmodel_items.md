# pygame-ce 実装用 画面ごとの ViewModel 項目一覧

- 文書ID: DOC-DSN-35A
- 最終更新日: 2026-04-27
- 文書種別: 実装言語別補助資料（Python / pygame-ce 向け）
- 関連文書:
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/03_internal_design/35_rendering_design.md`
  - `docs/03_internal_design/39_interface_contract.md`

## 1. 位置付けと目的

本書は、`Block_Puzzle_DocDD` の画面仕様および描画設計を元に、`pygame-ce` 実装時に **各画面でどの情報を ViewModel として renderer に渡すか** を整理した補助資料である。

本プロジェクトの正本仕様は言語非依存であるが、DocDD セミナーでの実装演習を円滑にするため、**本書は特定言語（Python / pygame-ce）向けの具体化資料**として扱う。

本資料の目的は、以下を明確にすること。

- 画面ごとに必要な表示要素
- 画面ごとに必要な数値・状態
- 共通で持つべき ViewModel 項目
- renderer が扱う範囲と、ゲームロジック側が持つべき範囲の分離

---

## 2. 基本方針

- renderer は **表示専用** とする
- ルール判定、衝突判定、スコア計算、T-Spin 判定そのものは ViewModel に含めない
- renderer は、ゲームロジック側が組み立てた `ScreenViewModel` を受け取って描画する
- 画面ごとに必要な項目だけを埋める
- 初回実装では、A-TYPE 主軸の必須 5 画面を対象とする

対象画面:

- SCR-001 タイトル画面
- SCR-002 A-TYPE 開始設定画面
- SCR-003 プレイ画面
- SCR-004 一時停止画面
- SCR-005 ゲームオーバー / リザルト画面

---

## 3. 共通 `ScreenViewModel` の考え方

各画面は、共通の `ScreenViewModel` をベースに持つ。ただし、全項目を全画面で使う必要はない。

### 3.1 共通項目案

| 項目 | 型イメージ | 用途 |
|---|---|---|
| `screen_state` | `str` | 現在画面の識別（`title`, `setup_a`, `play`, `pause`, `gameover`） |
| `rects` | `dict[str, tuple[int, int, int, int]]` | 描画領域矩形 |
| `labels` | `dict[str, str]` | 固定文言、見出し、案内 |
| `numeric_values` | `dict[str, int]` | SCORE / LEVEL / LINES などの数値 |
| `board_cells` | `list[dict]` | 固定済み盤面セル |
| `current_piece_cells` | `list[dict]` | 現在操作中ピースのセル |
| `next_piece_cells` | `list[dict]` | NEXT 表示用セル |
| `overlays` | `list[dict]` | `PAUSE`, `GAME OVER`, `T-SPIN` などの重ね表示 |
| `guides` | `list[str]` | キーガイドや操作案内 |
| `flags` | `dict[str, Any]` | `next_visible` などの表示フラグ |

### 3.2 参考データ構造

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ScreenViewModel:
    screen_state: str
    rects: dict[str, tuple[int, int, int, int]] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    numeric_values: dict[str, int] = field(default_factory=dict)
    board_cells: list[dict[str, Any]] = field(default_factory=list)
    current_piece_cells: list[dict[str, Any]] = field(default_factory=list)
    next_piece_cells: list[dict[str, Any]] = field(default_factory=list)
    overlays: list[dict[str, Any]] = field(default_factory=list)
    guides: list[str] = field(default_factory=list)
    flags: dict[str, Any] = field(default_factory=dict)
```

---

## 4. 画面ごとの ViewModel 項目一覧

### 4.1 SCR-001 タイトル画面

#### 表示目的
- タイトル表示
- A-TYPE 開始導線
- START 相当入力の案内
- 必要に応じて B-TYPE / 2P は予約であることを示す

#### 必須項目

| 項目 | 必須 | 内容 |
|---|:---:|---|
| `screen_state` | ○ | `title` |
| `labels["title"]` | ○ | タイトル名 |
| `labels["primary_action"]` | ○ | `PRESS START` 相当 |
| `labels["mode_hint"]` | ○ | `A-TYPE` |
| `labels["reserved_hint"]` | △ | `B-TYPE / 2P: RESERVED` など |
| `guides` | ○ | `START (Enter): NEXT SCREEN` など |

#### 不要項目
- `board_cells`
- `current_piece_cells`
- `next_piece_cells`
- `numeric_values`

```python
title_vm = ScreenViewModel(
    screen_state="title",
    labels={
        "title": "FALLING BLOCK PUZZLE",
        "primary_action": "PRESS START",
        "mode_hint": "A-TYPE",
        "reserved_hint": "B-TYPE / 2P: RESERVED",
    },
    guides=["START (Enter): NEXT SCREEN"],
)
```

### 4.2 SCR-002 A-TYPE 開始設定画面

#### 表示目的
- A-TYPE の開始レベル設定
- 開始確定と戻る導線の提示

#### 必須項目

| 項目 | 必須 | 内容 |
|---|:---:|---|
| `screen_state` | ○ | `setup_a` |
| `labels["mode"]` | ○ | `A-TYPE` |
| `labels["level_label"]` | ○ | `LEVEL` |
| `numeric_values["start_level"]` | ○ | 現在の開始レベル |
| `labels["confirm"]` | ○ | `A / START: BEGIN` |
| `labels["back"]` | ○ | `B: BACK` |
| `guides` | ○ | Left / Right 変更案内を含む |
| `flags["level_min"]` | △ | `0` |
| `flags["level_max"]` | △ | `9` |

#### 不要項目
- `board_cells`
- `current_piece_cells`
- `next_piece_cells`

```python
setup_a_vm = ScreenViewModel(
    screen_state="setup_a",
    labels={
        "mode": "A-TYPE",
        "level_label": "LEVEL",
        "confirm": "A / START: BEGIN",
        "back": "B: BACK",
    },
    numeric_values={"start_level": 0},
    guides=[
        "LEFT / RIGHT: CHANGE LEVEL",
        "A / START: BEGIN",
        "B: BACK",
    ],
    flags={"level_min": 0, "level_max": 9},
)
```

### 4.3 SCR-003 プレイ画面

#### 表示目的
- ゲームプレイ中の盤面と情報表示
- SCORE / LEVEL / LINES / NEXT の提示
- T-Spin など短時間メッセージ
- NEXT ON/OFF の切替反映

#### 必須項目

| 項目 | 必須 | 内容 |
|---|:---:|---|
| `screen_state` | ○ | `play` |
| `rects["playfield_cells"]` | ○ | 盤面領域 |
| `rects["side_panel_background"]` | ○ | 右側情報欄背景 |
| `rects["score_panel"]` | ○ | SCORE パネル |
| `rects["level_panel"]` | ○ | LEVEL パネル |
| `rects["lines_panel"]` | ○ | LINES パネル |
| `rects["next_panel"]` | ○ | NEXT パネル |
| `rects["status_message_anchor"]` | ○ | メッセージ表示アンカー |
| `labels["score"]` | ○ | `SCORE` |
| `labels["level"]` | ○ | `LEVEL` |
| `labels["lines"]` | ○ | `LINES` |
| `labels["next"]` | ○ | `NEXT` |
| `numeric_values["score"]` | ○ | 現在スコア |
| `numeric_values["level"]` | ○ | 現在レベル |
| `numeric_values["lines"]` | ○ | 累計ライン数 |
| `board_cells` | ○ | 固定済み盤面セル |
| `current_piece_cells` | ○ | 現在操作中ピース |
| `next_piece_cells` | △ | NEXT 表示が ON の場合 |
| `flags["next_visible"]` | ○ | NEXT 表示 ON/OFF |
| `overlays` | △ | `T-SPIN` など短時間メッセージ |
| `guides` | △ | キーガイド簡易表示 |

#### `rects` の基準値

```python
{
    "playfield_cells": (0, 0, 320, 576),
    "side_panel_background": (320, 0, 320, 576),
    "score_panel": (352, 48, 256, 112),
    "level_panel": (352, 184, 256, 112),
    "lines_panel": (352, 320, 256, 112),
    "next_panel": (352, 456, 256, 96),
    "status_message_anchor": (48, 16, 544, 32),
}
```

#### `board_cells` / `current_piece_cells` の 1 要素例

```python
{
    "col": 0,
    "row": 0,
    "tile_id": "I",
    "color_key": "cyan",
}
```

#### 非表示であるべき要素
- Hold 枠
- Hard drop 案内
- ゴーストピース
- 対戦用 UI

### 4.4 SCR-004 一時停止画面

#### 表示目的
- 停止中であることを明示
- 停止前盤面の静止表示
- 再開導線とタイトル復帰導線を表示

#### 必須項目

| 項目 | 必須 | 内容 |
|---|:---:|---|
| `screen_state` | ○ | `pause` |
| `rects` | ○ | プレイ画面と同一でよい |
| `labels` | ○ | プレイ画面のラベルを流用可 |
| `numeric_values` | ○ | SCORE / LEVEL / LINES の静止表示 |
| `board_cells` | ○ | 停止前盤面 |
| `overlays` | ○ | `PAUSE` 表示 |
| `guides` | ○ | 再開 / タイトル復帰案内 |
| `flags["input_locked"]` | △ | プレイ入力無効化フラグ |

### 4.5 SCR-005 ゲームオーバー / リザルト画面

#### 表示目的
- ゲーム終了を明示
- 最終盤面、最終 SCORE / LEVEL / LINES を表示
- 再試行導線とタイトル復帰導線を表示

#### 必須項目

| 項目 | 必須 | 内容 |
|---|:---:|---|
| `screen_state` | ○ | `gameover` |
| `rects` | ○ | プレイ画面と同一でよい |
| `labels` | ○ | プレイ画面のラベルを流用可 |
| `numeric_values` | ○ | 最終 SCORE / LEVEL / LINES |
| `board_cells` | ○ | 最終盤面の静止表示 |
| `overlays` | ○ | `GAME OVER` 表示 |
| `guides` | ○ | 再試行 / タイトル復帰案内 |

---

## 5. 予約画面の扱い

以下は現時点では予約画面であり、初回実装では未実装または stub でよい。

- SCR-006 モード選択画面
- SCR-007 B-TYPE 設定画面

したがって、初回の `ScreenViewModel` 実装対象からは外してよい。

---

## 6. renderer 側の分岐例

`pygame-ce` 実装では、renderer は `screen_state` を見て画面別描画関数へ分岐する。

```python
def render_screen(screen, vm: ScreenViewModel) -> None:
    if vm.screen_state == "title":
        render_title(screen, vm)
    elif vm.screen_state == "setup_a":
        render_setup_a(screen, vm)
    elif vm.screen_state == "play":
        render_play(screen, vm)
    elif vm.screen_state == "pause":
        render_pause(screen, vm)
    elif vm.screen_state == "gameover":
        render_gameover(screen, vm)
```

---

## 7. renderer に入れてはいけないもの

ViewModel / renderer へは以下を直接持ち込まない。

- 衝突判定ロジック
- T-Spin 判定ロジック
- スコア計算ロジック
- 自動落下タイマ制御
- raw な物理入力デバイス状態
- ゲーム進行状態を更新する責務

これらはゲームロジック側が担当し、renderer は **結果表示** に専念する。

---

## 8. 初回実装で最低限必要な項目まとめ

### 必須
- `screen_state`
- `rects`
- `labels`
- `numeric_values`
- `board_cells`
- `current_piece_cells`
- `next_piece_cells`
- `overlays`
- `guides`
- `flags["next_visible"]`

### 後回し可能
- 予約画面
- 高度な演出
- フォント PNG 資産を使った本格描画
- 装飾境界やサイドパネルの凝ったグラフィック

---

## 9. 補足

本一覧は、`21_ui_screen_spec.md` と `35_rendering_design.md` から `pygame-ce` 実装用に切り出した整理である。

主眼は、

- **どの画面で何を描くか**
- **何を ViewModel に載せるか**
- **何を renderer に載せてはいけないか**

を明確にし、DocDD 文書と Python コードを対応づけやすくすることにある。
