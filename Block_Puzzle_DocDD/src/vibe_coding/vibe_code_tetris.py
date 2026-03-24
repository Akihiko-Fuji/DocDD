"""
vibe_code_tetris.py
「短いリクエストひとつ」から生成したバイブコーディング成果物。
 
本ファイルは DocDD（文書駆動開発）の比較用サンプルとして保管する。
仕様書を参照せずに書かれたコードがどのような形になるかを示すのが目的であり、
DocDD の正本実装は src/DocDD_coding/ に置く。
 
操作方法:
    ← → キー : ピースを左右に動かす
    ↓ キー   : ピースを1段だけ落とす（ソフトドロップ）
    ↑ キー   : ピースを時計回りに90度回転させる
    r キー   : ゲームをリスタートする
 
【座標系に関する注意】
 SHAPES の定義は (x, y) 順のオフセットリストだが、cells() 内の回転処理は
 (y, 3-x) という軸の入れ替えを行っており、公式文書（24a_piece_shape_spawn_spec.md、
 33_data_model.md）の occupied_offsets 定義（dx=列方向, dy=行方向）とは
 座標軸の扱いが異なる。
 このズレは「仕様書なしで書くとこうなる」ことを示す教材として残してある。
"""
 
import tkinter as tk
import random
from pathlib import Path
 
# ─── 定数 ──────────────────────────────────────────────────────
CELL   = 24   # 1マスのピクセルサイズ（横・縦とも）
BOARD_W = 10  # 盤面の横マス数
BOARD_H = 18  # 盤面の縦マス数（公式仕様: 10×18）
TICK   = 400  # 自動落下の間隔（ミリ秒）。小さいほど速い
 
# 7種テトロミノの形状定義。各リストは「どのマスを占有するか」を (x, y) の組で表す。
# ※ この座標系は公式文書の定義と軸の扱いが異なる（ファイル冒頭の注意を参照）
SHAPES = [
    [(0,1),(1,1),(2,1),(3,1)],          # I ピース（横棒）
    [(1,0),(2,0),(1,1),(2,1)],          # O ピース（正方形）
    [(1,0),(0,1),(1,1),(2,1)],          # T ピース（T字）
    [(1,0),(2,0),(0,1),(1,1)],          # S ピース（右上がり段）
    [(0,0),(1,0),(1,1),(2,1)],          # Z ピース（左上がり段）
    [(0,0),(0,1),(1,1),(2,1)],          # J ピース（左上突起）
    [(2,0),(0,1),(1,1),(2,1)],          # L ピース（右上突起）
]
 

# ゲーム全体を管理するクラス
class Game:
    """
    ウィンドウの作成・キー入力の受付・盤面の状態管理・描画ループを
    ひとつのクラスにまとめている。
    インスタンスを作るだけでゲームが起動し、ウィンドウを閉じるまで動き続ける。
    """

 
    # ゲームの起動処理
    def __init__(self):
        """
        以下をまとめて行う:
          1. フォント画像の読み込み先を決める
          2. ウィンドウとキャンバス（描画エリア）を作る
          3. キーボード入力とゲーム操作を結び付ける
          4. フォントを読み込む
          5. 盤面を初期化してゲームループを開始する
        """
        # フォント画像（PNG グリフ）が置かれているフォルダを決める
        self.fontset_dir = Path(__file__).resolve().parent.parent / "art" / "fontset"
        # 文字 → PNG画像 の辞書（キー: 1文字の大文字、値: PhotoImage オブジェクト）
        self.font_glyphs = {}
        # loop() のたびに再描画するため、画像参照を保持するリスト（GCによる消去防止）
        self.font_image_refs = []
 
        # メインウィンドウを作る
        self.root = tk.Tk()
        # 描画エリア（キャンバス）を作る。盤面の下に1行分（32px）の案内表示を加えた高さにする
        self.canvas = tk.Canvas(
            self.root,
            width=CELL * BOARD_W,
            height=CELL * BOARD_H + 32,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()
 
        # キーボードの各キーに操作を割り当てる
        for key, func in [
            ("<Left>",  lambda e: self.move(-1)),     # 左移動
            ("<Right>", lambda e: self.move(1)),      # 右移動
            ("<Down>",  lambda e: self.move(0, 1)),   # 1段落下（ソフトドロップ）
            ("<Up>",    lambda e: self.move(0, 0, 1)),# 時計回り回転
            ("r",       self.reset),                  # リスタート
        ]:
            self.root.bind(key, func)
 
        # フォント読み込み → 盤面初期化 → ゲームループ開始 → ウィンドウを表示し続ける
        self.load_fontset()
        self.reset()
        self.loop()
        self.root.mainloop()

 
    # 盤面とピースを初期状態に戻す
    def reset(self, *_):
        """
        ゲーム開始時と、ゲームオーバー時（新ピースが置けないとき）に呼ばれる。
        盤面を全て空にして、新しいピースをランダムに選んで上部中央に配置する。
 
        ピースの状態は [形番号, x座標, y座標, 回転状態] の4要素リストで持つ。
        """
        # 盤面を全マス 0（空）で初期化する。0=空、1=固定済みブロック
        self.board = [[0] * BOARD_W for _ in range(BOARD_H)]
        # ピースを [形番号, 開始x, 開始y, 回転(0=初期姿勢)] で初期化する
        self.piece = [random.randrange(len(SHAPES)), 3, 0, 0]

 
    # ピースが現在占有している全マスの座標リストを返す
    def cells(self, piece=None):
        """
        引数にピース状態を渡した場合はそのピースで計算し、
        省略した場合は操作中の現在ピース（self.piece）で計算する。
        衝突判定・描画・固定のすべてでこのメソッドを使う。
 
        引数:
            piece: [形番号, x, y, 回転] のリスト。省略時は self.piece を使う。
 
        戻り値:
            [(x, y), ...] の形式で、ピースが占めているマス座標のリスト。
        """
        shape_id, px, py, rot = piece or self.piece
        cells = SHAPES[shape_id]
        # 回転を rot 回分だけ適用する（1回 = 時計回り90度）
        # (x, y) → (y, 3-x) という変換が1回の時計回り回転に対応する
        for _ in range(rot):
            cells = [(y, 3 - x) for x, y in cells]
        # 形状の相対座標にピースの現在位置を加算して絶対座標に変換する
        return [(px + x, py + y) for x, y in cells]

 
    # 指定した座標リストが「壁・床・固定済みブロック」に衝突するか判定する
    def hit(self, cells):
        """
        引数:
            cells: [(x, y), ...] の形式のマス座標リスト。
 
        戻り値:
            衝突していれば True、していなければ False。
        """
        return any(
            x < 0 or x >= BOARD_W      # 左右の壁を超える
            or y < 0 or y >= BOARD_H   # 上下の壁・床を超える
            or self.board[y][x]        # すでに固定されているブロックと重なる
            for x, y in cells
        )


    # ピースを移動または回転させる処理
    def move(self, dx=0, dy=0, rot=0):
        """
        移動・回転後の位置が有効（壁・固定ブロックに当たらない）なら
        その位置に更新する。有効でない場合は:
          - 下方向への移動が失敗した場合 → 接地したとみなして lock() を呼ぶ
          - それ以外（左右・回転の失敗）  → 何もしない（入力を無視する）
 
        引数:
            dx : 横方向の移動量（-1=左, +1=右, 0=移動なし）
            dy : 縦方向の移動量（+1=1段下, 0=移動なし）
            rot: 回転量（1=時計回り1回, 0=回転なし）
        """
        # 現在のピース状態をコピーして、移動・回転を仮適用する
        next_piece = self.piece[:]
        next_piece[1] += dx                          # x座標を横移動
        next_piece[2] += dy                          # y座標を縦移動
        next_piece[3] = (next_piece[3] + rot) % 4   # 回転状態を更新（0〜3 で循環）
 
        if self.hit(self.cells(next_piece)):
            # 衝突した場合
            if dy:
                # 下方向への移動が衝突 = 床か積み上がりに当たった = 固定処理へ
                self.lock()
        else:
            # 衝突しなければ、仮適用した位置を正式に採用する
            self.piece = next_piece


    # 現在ピースを盤面に固定し、ライン消去と次のピース出現を行う
    def lock(self):
        """
        処理の流れ:
          1. 現在ピースのマスを盤面に書き込む（0→1）
          2. 横一列が全て埋まった行（完成ライン）を消去する
          3. 消去した行数だけ、上から空行を追加して盤面を詰める
          4. 次のピースをランダムに出現させる
          5. 新しいピースがすでに盤面に当たる（=積み上がりすぎ）なら reset() する
        """
        # ピースのマスを盤面に書き込む
        for x, y in self.cells():
            self.board[y][x] = 1
 
        # 完成していない行（0が1つ以上含まれる行）だけを残す → 完成行が自動的に消える
        self.board = [row for row in self.board if 0 in row]
 
        # 消えた行の分だけ、盤面の上に空行を追加して高さを元に戻す
        cleared = BOARD_H - len(self.board)  # 消えた行数
        self.board = [[0] * BOARD_W for _ in range(cleared)] + self.board
 
        # 次のピースをランダムに選んで上部中央に出現させる
        self.piece = [random.randrange(len(SHAPES)), 3, 0, 0]
 
        # 出現直後から衝突していれば、積み上がりすぎでゲームオーバー → リセット
        if self.hit(self.cells()):
            self.reset()

    # art/fontset フォルダから PNG グリフ画像を読み込む
    def load_fontset(self):
        """
        フォルダが存在しない場合は何もしない（フォールバックで通常テキスト表示になる）。
        ファイル名が1文字（例: A.png, 0.png）のものだけを対象とし、
        self.font_glyphs に「文字 → 画像」の辞書として保存する。
        """
        if not self.fontset_dir.exists():
            # フォルダがなければスキップ（フォントなしでも動作する）
            return
        for png in self.fontset_dir.glob("*.png"):
            char = png.stem.upper()          # ファイル名から拡張子を除いた1文字を取得
            if len(char) != 1:
                continue                     # 複数文字のファイル名（ex.png など）は除外
            self.font_glyphs[char] = tk.PhotoImage(file=str(png))

    # 指定した座標にテキストを固定幅フォントで描画する
    def draw_fixed_text(self, x, y, text):
        """
        PNG グリフが読み込まれていれば 1文字=32px の固定幅で並べて描画する。
        グリフがなければ tkinter 標準のテキスト描画にフォールバックする。
        小文字が渡された場合は大文字に正規化してから描画する（仕様準拠）。
 
        引数:
            x   : 描画開始位置の左端 x 座標（ピクセル）
            y   : 描画開始位置の上端 y 座標（ピクセル）
            text: 描画する文字列
        """
        # 仕様に合わせ、英小文字は大文字に正規化してから描画する
        normalized = text.upper()
 
        if not self.font_glyphs:
            # PNG グリフが読み込まれていない場合は通常のテキスト描画で代替する
            self.canvas.create_text(x, y, text=normalized, fill="white", anchor="nw")
            return
 
        cursor_x = x  # 文字を置いていく現在のx位置
        for char in normalized:
            if char == " ":
                cursor_x += 32  # スペースは1文字分だけ右にずらして何も描かない
                continue
            glyph = self.font_glyphs.get(char)
            if glyph is not None:
                self.canvas.create_image(cursor_x, y, image=glyph, anchor="nw")
                # tkinter のガベージコレクション対策として参照を保持しておく
                self.font_image_refs.append(glyph)
            cursor_x += 32  # 次の文字の位置に進む（グリフが存在しない文字も幅分だけ空ける）

    # ゲームの1フレーム分の処理をまとめて行い、次フレームを予約する
    def loop(self):
        """
        TICK ミリ秒ごとに繰り返し呼ばれ続けることでゲームが進行する。
        毎回キャンバスを全消去してから再描画するため、前フレームの残像は残らない。
 
        処理の流れ:
          1. 画面を全消去する
          2. 固定済みブロックを白い四角で描く
          3. 現在ピースをシアン（水色）の四角で描く
          4. 画面下部にキー案内テキストを描く
          5. ピースを1段自動落下させる（衝突すれば lock() が呼ばれる）
          6. TICK ミリ秒後に再びこの関数を呼ぶよう予約する
        """
        # 前フレームの描画内容を全て消去する
        self.canvas.delete("all")
        # 画像参照リストも毎フレームリセットする（再描画のたびに追加していくため）
        self.font_image_refs = []
 
        # 固定済みブロックを白い四角で描く
        [
            self.canvas.create_rectangle(
                x * CELL, y * CELL, x * CELL + CELL, y * CELL + CELL,
                fill="white", outline="#222"
            )
            for y, row in enumerate(self.board)
            for x, value in enumerate(row)
            if value  # value=1 のマスだけ描く
        ]
 
        # 操作中の現在ピースをシアン（水色）の四角で描く
        [
            self.canvas.create_rectangle(
                x * CELL, y * CELL, x * CELL + CELL, y * CELL + CELL,
                fill="cyan", outline="#222"
            )
            for x, y in self.cells()
        ]
 
        # 盤面の下にキー操作の案内テキストを描く
        self.draw_fixed_text(0, CELL * BOARD_H, "r:restart")
 
        # ピースを1段下に自動落下させる（衝突すれば lock() が呼ばれる）
        self.move(0, 1)
 
        # TICK ミリ秒後に再びこの関数を呼ぶことでゲームループが続く
        self.root.after(TICK, self.loop)
 
 
# ゲームを開始する（このファイルを実行するとここが呼ばれる）
Game()
