# DocDD_coding 実装

本実装は `docs/` を一次情報にした DocDD 正本実装（A-TYPE最小版）です。

## 対応主要文書
- DOC-SPC-020/021/022/023/023a/024/024a/025
- DOC-DSN-030/032/034/035/036/039
- QA 40/41/42/43

## 実行方法
```bash
cd Block_Puzzle_DocDD
pip install -r requirements.txt
python src/DocDD_coding/main.py
```

## テスト
```bash
cd Block_Puzzle_DocDD
python -m pytest tests/DocDD_coding
```

## 実装済み範囲
- TITLE/SETUP_A/PLAY/PAUSE/GAMEOVER
- `art/artwork/*.png` の背景・壁・ブロック画像を優先利用（失敗時は矩形描画へフォールバック）
- `art/fontset/*.png` の文字単位透過PNGを HUD/画面文言の描画に利用（不足時は標準フォントへフォールバック）
- 10x18盤面、7種ピース、NEXT 1個、SELECTでNEXT表示切替
- A/B回転、左右、Downソフトドロップ、自動落下
- 固定、ライン消去、得点、レベル進行、T-Spin判定/得点

## 未実装範囲
- B-TYPE本実装、対戦、保存UI、replay UI

## implementation notes
- ランダマイザは非7-bagを満たすため Python `random.choice` ベースで seed 再現可能実装を採用。
- 通常固定後は ARE 10フレーム、ライン消去時は点滅20フレーム＋ARE 10フレームを適用。
- ソフトドロップと通常落下は独立タイマで管理し、Down中の二重落下を防止。


## ドキュメント整合性
- `DOC-SPC-024a` の T ピース rotation=0 の occupied_offsets は、同文書 5.3 の出現絶対座標例および本実装と整合するよう修正済みです。
- 乱数器の「Game Boy 実機アルゴリズム」厳密値は文書に未定義のため、非7-bag・seed再現可能という文書要件を満たす実装で補完しています。

## 既知の制限
- 画像/文字アセット読込に失敗した場合はフォールバック描画（矩形/標準フォント）へ切替。
- replay/config 永続化は未実装。
- `art/fontset` の現物は16×16pxであり、32×32px表示が必要な箇所では整数倍拡大して使用する。

## vibe_codingとの差分
- `src/vibe_coding/` は比較用で未編集。本実装は `src/DocDD_coding/` のみ。
- 外観面: アート画像とビットマップフォントを優先利用し、未配置時のみフォールバックする二段構えにしている。
- 保守面: 画像読込失敗理由を `asset_errors` に収集し、タイトル画面でフォールバック稼働中を可視化できる。

## 注意
- 商用ゲーム複製を目的としません。
- 外部著作物（画像/音声/フォント）を同梱しません。
