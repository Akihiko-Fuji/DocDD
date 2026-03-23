# 描画設計 / Rendering Design

- 文書ID: DOC-DSN-035
- 最終更新日: 2026-03-23
- 関連文書:
  - `21_ui_screen_spec.md`
  - `34_module_design.md`

## 1. 目的
UI 仕様で求める表示要素を、描画責務としてどのように保持するかを定義する。

## 2. 方針
- 盤面視認性を優先する
- 盤面、NEXT、SCORE、LINES、LEVEL を安定表示する
- 装飾素材は差し替え可能とする
- Game Boy 版由来の簡潔さを崩す追加表示は避ける

## 3. 描画責務
- プレイ画面の必須情報を欠落させない
- pause / game over の状態表示をゲーム進行と矛盾させない
- T-Spin 成立表示を短時間・簡潔に提示できるようにする
- Hold 枠、Hard drop 案内、ghost 表示を生成しない

## 4. 入出力
- 入力: `GameSession`, 状態種別, 必要な表示メッセージ
- 出力: 画面描画命令または view model

## 5. 受入観点
- `21_ui_screen_spec.md` の必須表示要素と一致すること
- ルール判定が renderer 側へ混入していないこと
- 非採用 UI 要素が描画設計から除外されていること
