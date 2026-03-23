# 最小の説明要件で構築したバイブコーディングによる60行のコード。 ←→:移動 ↑:回転 ↓:1段落下 r:リスタート
import tkinter as tk
import random

CELL, BOARD_W, BOARD_H, TICK = 24, 10, 20, 400
SHAPES = [
    [(0,1),(1,1),(2,1),(3,1)], [(1,0),(2,0),(1,1),(2,1)], [(1,0),(0,1),(1,1),(2,1)],
    [(1,0),(2,0),(0,1),(1,1)], [(0,0),(1,0),(1,1),(2,1)], [(0,0),(0,1),(1,1),(2,1)],
    [(2,0),(0,1),(1,1),(2,1)],
]

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=CELL*BOARD_W, height=CELL*BOARD_H, bg="black", highlightthickness=0)
        self.canvas.pack()
        for key, func in [
            ("<Left>", lambda e: self.move(-1)), ("<Right>", lambda e: self.move(1)),
            ("<Down>", lambda e: self.move(0, 1)), ("<Up>", lambda e: self.move(0, 0, 1)),
            ("r", self.reset)
        ]: self.root.bind(key, func)
        self.reset(); self.loop(); self.root.mainloop()

    def reset(self, *_):
        self.board = [[0] * BOARD_W for _ in range(BOARD_H)]
        self.piece = [random.randrange(len(SHAPES)), 3, 0, 0]

    def cells(self, piece=None):
        shape_id, px, py, rot = piece or self.piece
        cells = SHAPES[shape_id]
        for _ in range(rot): cells = [(y, 3 - x) for x, y in cells]
        return [(px + x, py + y) for x, y in cells]

    def hit(self, cells):
        return any(x < 0 or x >= BOARD_W or y < 0 or y >= BOARD_H or self.board[y][x] for x, y in cells)

    def move(self, dx=0, dy=0, rot=0):
        next_piece = self.piece[:]
        next_piece[1] += dx; next_piece[2] += dy; next_piece[3] = (next_piece[3] + rot) % 4
        if self.hit(self.cells(next_piece)):
            if dy: self.lock()
        else: self.piece = next_piece

    def lock(self):
        for x, y in self.cells(): self.board[y][x] = 1
        self.board = [row for row in self.board if 0 in row]
        self.board = [[0] * BOARD_W for _ in range(BOARD_H - len(self.board))] + self.board
        self.piece = [random.randrange(len(SHAPES)), 3, 0, 0]
        if self.hit(self.cells()): self.reset()

    def loop(self):
        self.canvas.delete("all")
        [self.canvas.create_rectangle(x*CELL, y*CELL, x*CELL+CELL, y*CELL+CELL, fill="white", outline="#222")
         for y, row in enumerate(self.board) for x, value in enumerate(row) if value]
        [self.canvas.create_rectangle(x*CELL, y*CELL, x*CELL+CELL, y*CELL+CELL, fill="cyan", outline="#222")
         for x, y in self.cells()]
        self.move(0, 1)
        self.root.after(TICK, self.loop)

Game()