# アーキテクチャ設計 / Architecture Design

- 文書ID: DOC-DSN-030
- 最終更新日: 2026-03-24
- 関連文書:
  - `27_runtime_flowchart_mermaid.md`
  - `32_state_machine_design.md`
  - `34_module_design.md`
  - `35_rendering_design.md`
  - `37_error_handling_policy.md`

## 1. 目的
外部仕様を実装へ落とすための上位アーキテクチャ境界を定義し、責務混在を防ぐ。

## 2. 構成方針
- Input
- State Machine
- Runtime Flow Visualization
- Game Rules
- Rendering
- Persistence（予約）

外部仕様と内部責務の対応を保つため、ゲーム進行と描画を分離する。

## 3. 層構成
```text
Physical Input
  -> Input Mapping
  -> State Control
  -> Session / Rule Services
  -> Render View Model
  -> Screen Output
```

## 4. アーキテクチャ原則
1. 入力解釈は状態遷移より前でなく、`state_controller` の判断と整合すること
2. ルール処理は renderer に持ち込まないこと
3. persistence は現行 build では予約だが、`config.ini` と replay の構造は文書で先行固定すること
4. Game Boy 基準で不足する事項を補完した場合は、ADR か仕様へ必ず反映すること

## 5. 主要データ流れ
- 入力は `InputSnapshot` に正規化してから状態制御へ渡す
- ルール処理は `GameSession` と `ScoreState` を中心に進む
- 描画は `SessionView` または同等の view model を正本とする
- 表示基準解像度は 640×480 とし、PC 利用前提の固定基準解像度とする

## 6. 受入観点
- Input / State / Rules / Rendering / Persistence 予約の境界が読めること
- `34_module_design.md` のモジュール一覧へ自然に接続できること
- Diagram-Driven 観点で `38_runtime_state_transition_mermaid.md` と矛盾しないこと
