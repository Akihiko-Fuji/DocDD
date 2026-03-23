# ランタイムフローチャート図（Mermaid） / Runtime Flowchart Diagram (Mermaid)

- 文書ID: DOC-SPC-027
- 最終更新日: 2026-03-23
- 目的: 画面遷移とプレイフレーム内の判断順序を Mermaid フローチャートで可視化し、外部仕様レビューを補助する
- 関連文書:
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`

---

## 1. 本書の位置付け
本書は外部仕様補助文書であり、画面要件の正本は `21_ui_screen_spec.md`、入力の正本は `22_input_operation_spec.md`、一時停止・ゲームオーバー仕様の正本は `25_pause_gameover_resume_spec.md`、内部責務の正本は `32_state_machine_design.md` が保持する。
本書は、これらの文書を横断して主要フローを Mermaid で視覚化した補助資料である。

---

## 2. 画面遷移フローチャート
```mermaid
flowchart TD
    A[起動] --> B[タイトル画面<br/>SCR-001]
    B -->|START相当入力| C[A-TYPE開始設定画面<br/>SCR-002]
    C -->|Left / Right| C
    C -->|A または START| D[プレイ画面<br/>SCR-003]
    C -->|B| B
    D -->|START| E[一時停止画面<br/>SCR-004]
    E -->|START| D
    E -->|B / ESC| B
    D -->|出現不能| F[ゲームオーバー/リザルト画面<br/>SCR-005]
    F -->|START または A| C
    F -->|B / ESC| B
```

---

## 3. プレイフレーム処理フローチャート
```mermaid
flowchart TD
    P0[フレーム開始] --> P1[入力スナップショット取得]
    P1 --> P2[状態に応じて有効入力を抽出]
    P2 --> P3{START入力あり?}
    P3 -->|Yes| P4[ST-PAUSEへ遷移]
    P3 -->|No| P5[回転を評価]
    P5 --> P6[左右移動を評価]
    P6 --> P7[Downを評価]
    P7 --> P8[自動落下評価]
    P8 --> P9{下移動不能か?}
    P9 -->|No| P10[描画更新して次フレームへ]
    P9 -->|Yes| P11[固定処理へ進む]
    P11 --> P12[完成ライン判定と消去]
    P12 --> P13[T-Spin判定・得点・ライン・レベル更新]
    P13 --> P14[NEXT繰上げと新NEXT補充]
    P14 --> P15{次ピースを出現できるか?}
    P15 -->|Yes| P16[次ピース出現準備]
    P16 --> P10
    P15 -->|No| P17[ST-GAMEOVERへ遷移]
```

---

## 4. Diagram-Driven レビュー時の確認観点
1. 画面フローが `21_ui_screen_spec.md` の画面遷移表と一致していること
2. 開始設定画面の入力が `Left / Right` に統一されていること
3. 一時停止中に通常プレイ入力へ戻らないことが図から読めること
4. プレイフレーム内で START による一時停止判定が優先されていること
5. 出現不能時にゲームオーバーへ遷移することが明示されていること
