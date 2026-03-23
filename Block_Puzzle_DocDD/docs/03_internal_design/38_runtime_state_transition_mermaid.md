# ランタイム状態遷移図（Mermaid） / Runtime State Transition Diagram (Mermaid)

- 文書ID: DOC-DSN-038
- 最終更新日: 2026-03-23
- 目的: `32_state_machine_design.md` の上位状態および `ST-PLAY` サブ状態を Mermaid 図で可視化し、レビュー時の読解負荷を下げる
- 関連文書:
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`

---

## 1. 本書の位置付け
本書は内部設計補助文書であり、状態定義・責務・受入観点の正本は `32_state_machine_design.md` が保持する。
本書は、その設計内容を Mermaid 記法で確認できるようにした派生図である。

---

## 2. 上位状態遷移図
```mermaid
stateDiagram-v2
    [*] --> ST_BOOT : 起動
    ST_BOOT : ST-BOOT\n起動準備
    ST_TITLE : ST-TITLE\nタイトル
    ST_SETUP_A : ST-SETUP-A\nA-TYPE開始設定
    ST_PLAY : ST-PLAY\nプレイ中
    ST_PAUSE : ST-PAUSE\n一時停止
    ST_GAMEOVER : ST-GAMEOVER\nゲームオーバー/リザルト
    ST_MODE_SELECT : ST-MODE-SELECT\nモード選択(予約)
    ST_SETUP_B : ST-SETUP-B\nB-TYPE設定(予約)

    ST_BOOT --> ST_TITLE : 初期化完了
    ST_TITLE --> ST_SETUP_A : START相当入力
    ST_SETUP_A --> ST_PLAY : 開始確定
    ST_SETUP_A --> ST_TITLE : B / 戻る
    ST_PLAY --> ST_PAUSE : START
    ST_PAUSE --> ST_PLAY : START
    ST_PAUSE --> ST_TITLE : B / ESC
    ST_PLAY --> ST_GAMEOVER : 出現不能
    ST_GAMEOVER --> ST_SETUP_A : START / A で再試行
    ST_GAMEOVER --> ST_TITLE : B / ESC でタイトル復帰

    note right of ST_MODE_SELECT
        将来のA/B選択導入用予約状態
        現行 build では未接続
    end note
    note right of ST_SETUP_B
        将来のB-TYPE開始設定用予約状態
        現行 build では未接続
    end note
```

---

## 3. ST-PLAY サブ状態遷移図
```mermaid
stateDiagram-v2
    [*] --> PL_SPAWN
    PL_SPAWN : PL-SPAWN\n出現
    PL_ACTIVE : PL-ACTIVE\n操作/落下
    PL_LOCK_CHECK : PL-LOCK-CHECK\n接地/固定判定
    PL_CLEAR : PL-CLEAR\nライン消去
    PL_SCORE : PL-SCORE\n得点処理
    PL_NEXT : PL-NEXT\n次ピース準備
    PL_END_CHECK : PL-END-CHECK\n終了判定

    PL_SPAWN --> PL_ACTIVE : 出現成功
    PL_SPAWN --> ST_GAMEOVER : 出現不能
    PL_ACTIVE --> PL_ACTIVE : 回転 -> 左右 -> Down -> 自動落下
    PL_ACTIVE --> PL_LOCK_CHECK : 下移動不能
    PL_LOCK_CHECK --> PL_CLEAR : 固定成立
    PL_CLEAR --> PL_SCORE : 消去対象確定
    PL_SCORE --> PL_NEXT : T-Spin判定 / 得点 / ライン / レベル更新完了
    PL_NEXT --> PL_END_CHECK : NEXT繰上げ完了
    PL_END_CHECK --> PL_SPAWN : 継続可能
    PL_END_CHECK --> ST_GAMEOVER : 次出現不能
```

---

## 4. Diagram-Driven レビュー時の確認観点
1. 上位状態と画面遷移が `21_ui_screen_spec.md` と矛盾していないこと
2. 一時停止・ゲームオーバー遷移が `25_pause_gameover_resume_spec.md` と一致していること
3. T-Spin 判定責務が `PL-SCORE` に置かれていること
4. 予約状態が現行フローへ未接続であることが読み取れること
5. サブ状態図の入力順が `32_state_machine_design.md` と一致すること
