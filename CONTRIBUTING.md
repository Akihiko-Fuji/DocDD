# Contributing to DocDD

DocDDへの改善提案を歓迎します。本リポジトリでは、コードだけでなく、その判断根拠となる文書とテストの整合を重視します。

## 変更前に確認すること

1. [`START_HERE.md`](./START_HERE.md) で教材全体の位置づけを確認する。
2. 対象教材のREADMEとQuick Startを読む。
3. 大きな仕様変更は、先にIssueで目的・対象範囲・非対象を共有する。

## 変更の原則

- 既存文書の章構成や説明を、理由なく削除しない。
- 仕様を変更した場合は、関連する要求・設計・試験・変更記録を同じPRで更新する。
- `Block_Puzzle_DocDD/src/DocDD_coding/` を正本実装、`src/vibe_coding/` を比較用成果物として扱う。
- 実在する個人・企業・受注・生産実績・認証情報をサンプルへ含めない。
- 自作または再配布条件を確認できる画像だけを追加し、[`Block_Puzzle_DocDD/ASSETS.md`](./Block_Puzzle_DocDD/ASSETS.md) に出所と条件を記録する。

## ローカル検証

```bash
cd Block_Puzzle_DocDD
python -m pip install -r requirements.txt
python -m pytest tests/DocDD_coding src/DocDD_coding/test_tspin_lock_integration.py -q

cd ../results_record_db
python -m pip install -r requirements.txt
python -m pytest -q

cd ..
python scripts/check_repository.py
```

Pythonコードを変更した場合は、Ruffによる検査も推奨します。

```bash
ruff check Block_Puzzle_DocDD/src Block_Puzzle_DocDD/tests results_record_db/src results_record_db/tests results_record_db/sample_data/generate_sample_data.py
```

## Pull Request

PRには次を記載してください。

- 何を変更したか
- なぜ必要か
- 文書・実装・テストへの影響
- 実行した検証と結果
- 今回扱わない範囲

小さく追跡可能な変更を優先し、CIがすべて成功した状態でレビューを依頼してください。
