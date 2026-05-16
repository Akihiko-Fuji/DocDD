#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################################
# Name    : ingest_cli.py
# Author  : Akihiko Fujita
# Update  : 2026-05-20
############################################################################

"""results_record_db 取り込み処理の CLI エントリポイント。

主な責務:
- コマンドライン引数を解釈して入力ファイルとマスタを受け取る
- DB セッションを確立して ingest モジュールの実行を制御
- 実行サマリと終了コードを標準出力・標準エラーへ整形して返す

"""
from __future__ import annotations

import argparse
import sys

from db import get_session
from ingest import ingest_file, load_order_product_master


def build_parser() -> argparse.ArgumentParser:
    """CLI引数を定義する（source_systemは ingest.py 側のファイル名判定に委譲）。"""
    parser = argparse.ArgumentParser(
        description="Ingest one results_record_db input file."
    )
    parser.add_argument("file_path", help="Path to input file")
    parser.add_argument(
        "--order-product-master",
        dest="order_product_master",
        default=None,
        help="Path to order_product_master.csv for product_name lookup",
    )
    return parser


def main() -> int:
    """CLI の主処理を実行し、終了コードを返す。"""
    args = build_parser().parse_args()

    try:
        order_product_map = load_order_product_master(args.order_product_master)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ingest_error master message={exc}", file=sys.stderr)
        return 2
    try:
        with get_session() as session:
            result = ingest_file(
                session=session,
                file_path=args.file_path,
                order_product_map=order_product_map,
            )

        # 実行結果はサマリのみ標準出力に表示する。
        print(
            "ingest_summary "
            f"file={result.source_file_name} "
            f"batch_id={result.ingest_batch_id} "
            f"inserted={result.inserted} "
            f"rejected={result.rejected}"
        )
        return 0
    except ValueError as exc:
        print(f"ingest_error input message={exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        # エラー時は標準エラー出力に要約を出し、終了コード1を返す。
        print(f"ingest_error message={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
