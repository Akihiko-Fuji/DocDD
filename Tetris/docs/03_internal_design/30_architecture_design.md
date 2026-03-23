# アーキテクチャ設計 / Architecture Design

- 文書ID: DOC-DSN-030
- 最終更新日: 2026-03-23

## 構成方針
- Input
- Game Rules
- State Machine
- Rendering
- Persistence (予約)

外部仕様と内部責務の対応を保つため、ゲーム進行と描画を分離する。
