#!/usr/bin/env python3
"""Public-repository checks that require only the Python standard library."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".git", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
DOCUMENT_ID_RE = re.compile(r"^- 文書ID:\s*(\S+)\s*$", re.MULTILINE)
IMAGE_SIGNATURES = {
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".gif": (b"GIF87a", b"GIF89a"),
}


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts)
    )


def local_link_target(raw_target: str) -> str | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    # Markdown permits an optional title after the URL. Repository paths contain no spaces.
    target = target.split(maxsplit=1)[0]
    return unquote(target.split("#", 1)[0]) or None


def main() -> int:
    errors: list[str] = []
    doc_ids: list[tuple[str, Path]] = []

    for path in markdown_files():
        relative = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{relative}: Markdown must be UTF-8 text")
            continue

        for raw_target in LINK_RE.findall(text):
            target = local_link_target(raw_target)
            if target is None:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"{relative}: local link escapes repository: {raw_target}")
                continue
            if not resolved.exists():
                errors.append(f"{relative}: broken local link: {raw_target}")

        if "Block_Puzzle_DocDD/docs" in relative.as_posix():
            match = DOCUMENT_ID_RE.search(text)
            if match:
                doc_ids.append((match.group(1), relative))

    counts = Counter(doc_id for doc_id, _ in doc_ids)
    for doc_id, count in sorted(counts.items()):
        if count > 1:
            locations = ", ".join(str(path) for current, path in doc_ids if current == doc_id)
            errors.append(f"duplicate document ID {doc_id}: {locations}")

    docs_root = ROOT / "Block_Puzzle_DocDD" / "docs"
    for path in sorted(docs_root.iterdir()):
        if path.is_file():
            errors.append(f"{path.relative_to(ROOT)}: place canonical documents in a numbered subdirectory")

    for path in sorted(ROOT.rglob("*")):
        signatures = IMAGE_SIGNATURES.get(path.suffix.lower())
        if signatures is None or not path.is_file():
            continue
        header = path.read_bytes()[:8]
        if not any(header.startswith(signature) for signature in signatures):
            errors.append(f"{path.relative_to(ROOT)}: content does not match image extension")

    if errors:
        print("Repository quality checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Repository quality checks passed ({len(markdown_files())} Markdown files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
