import sys

from falling_block_puzzle.app import run


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"[ENTRYPOINT_ERROR] {type(exc).__name__}: {exc}")
        sys.exit(1)
