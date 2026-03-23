# ドメインモデル / Domain Model

- 文書ID: DOC-DSN-031
- 最終更新日: 2026-03-23

## 主要概念
| 概念 | 説明 |
|---|---|
| GameSession | 1 回のプレイ単位。モード、状態、スコア等を保持 |
| Board | 10×18 の盤面 |
| CurrentPiece | 現在操作中のピース |
| NextQueue | 1 個先の NEXT 管理 |
| ScoreState | SCORE / LINES / LEVEL を保持 |
| InputSnapshot | フレーム単位の入力状態 |
| PauseState | 一時停止中かどうか |
| TSpinResult | T-Spin 成立有無と消去ライン数 |

## 関係
- GameSession は Board, CurrentPiece, NextQueue, ScoreState を持つ
- CurrentPiece は PieceKind, Position, Rotation を持つ
- TSpinResult は CurrentPiece の固定後に ScoreState 更新へ渡す

## DocDD 追跡で特に重要な概念
- `GameSession`: 状態遷移、スコア、盤面を束ねる集約
- `InputSnapshot`: UI / 入力仕様から内部契約へ接続する橋渡し概念
- `TSpinResult`: 外部仕様の T-Spin 条件を得点処理へ接続する概念
- `ScoreState`: A-TYPE の LINES / LEVEL / SCORE を一体で保持する概念
