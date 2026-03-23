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
