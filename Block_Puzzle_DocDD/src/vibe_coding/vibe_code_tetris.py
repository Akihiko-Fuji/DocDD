"""
vibe_code_tetris.py
===================
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
 
# ─── 定数 ──────────────────────────────────────────────────────
CELL   = 24
BOARD_W = 10
BOARD_H = 18
TICK   = 400
 
# 7種テトロミノの形状定義。各リストは「どのマスを占有するか」を (x, y) の組で表す。
# ※ この座標系は公式文書の定義と軸の扱いが異なる（ファイル冒頭の注意を参照）
SHAPES = [
    [(0,1),(1,1),(2,1),(3,1)],
    [(1,0),(2,0),(1,1),(2,1)],
    [(1,0),(0,1),(1,1),(2,1)],
    [(1,0),(2,0),(0,1),(1,1)],
    [(0,0),(1,0),(1,1),(2,1)],
    [(0,0),(0,1),(1,1),(2,1)],
    [(2,0),(0,1),(1,1),(2,1)],
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
          1. ウィンドウとキャンバス（描画エリア）を作る
          2. キーボード入力とゲーム操作を結び付ける
          3. 盤面を初期化してゲームループを開始する
        """
        self.root = tk.Tk()
        self.canvas = tk.Canvas(
            self.root,
            width=CELL * BOARD_W,
            height=CELL * BOARD_H + 32,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()
 
        for key, func in [
            ("<Left>",  lambda e: self.move(-1)),
            ("<Right>", lambda e: self.move(1)),
            ("<Down>",  lambda e: self.move(0, 1)),
            ("<Up>",    lambda e: self.move(0, 0, 1)),
            ("r",       self.reset),
        ]:
            self.root.bind(key, func)

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
        self.board = [[0] * BOARD_W for _ in range(BOARD_H)]
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
        for _ in range(rot):
            cells = [(y, 3 - x) for x, y in cells]
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
            x < 0 or x >= BOARD_W
            or y < 0 or y >= BOARD_H
            or self.board[y][x]
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
        next_piece = self.piece[:]
        next_piece[1] += dx
        next_piece[2] += dy
        next_piece[3] = (next_piece[3] + rot) % 4

        if self.hit(self.cells(next_piece)):
            if dy:
                self.lock()
        else:
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
        for x, y in self.cells():
            self.board[y][x] = 1
 
        self.board = [row for row in self.board if 0 in row]
 
        cleared = BOARD_H - len(self.board)
        self.board = [[0] * BOARD_W for _ in range(cleared)] + self.board
 
        self.piece = [random.randrange(len(SHAPES)), 3, 0, 0]
 
        if self.hit(self.cells()):
            self.reset()

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
        self.canvas.delete("all")
 
        [
            self.canvas.create_rectangle(
                x * CELL, y * CELL, x * CELL + CELL, y * CELL + CELL,
                fill="white", outline="#222"
            )
            for y, row in enumerate(self.board)
            for x, value in enumerate(row)
            if value
        ]
 
        [
            self.canvas.create_rectangle(
                x * CELL, y * CELL, x * CELL + CELL, y * CELL + CELL,
                fill="cyan", outline="#222"
            )
            for x, y in self.cells()
        ]
 
        self.canvas.create_text(0, CELL * BOARD_H, text="r:restart", fill="white", anchor="nw")
 
        self.move(0, 1)
 
        self.root.after(TICK, self.loop)
 
 
# ゲームを開始する（このファイルを実行するとここが呼ばれる）
Game()
