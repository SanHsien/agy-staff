#!/usr/bin/env python3
"""檢查本 fork overlay 文件之間的相對連結。

驗證 FORK.md、NOTICE.md、REVIEW.md、AGENTS.md、SECURITY.md、
CONTRIBUTING.md、README.md、README.en.md 與 docs/ 內文件的相對連結。

    python tools/check_links.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_PATTERN = re.compile(r"""(?is)<img[^>]+src=["']([^"']+)["']""")
FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN_PATTERN = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")
SKIP_NAMES = {
    "upstream-review-report.md",
    "dependency-freshness-report.md",
}

FORK_DOCUMENTS = [
    ROOT / "FORK.md",
    ROOT / "NOTICE.md",
    ROOT / "REVIEW.md",
    ROOT / "AGENTS.md",
    ROOT / "SECURITY.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "README.md",
    ROOT / "README.en.md",
    ROOT / "docs" / "DECISIONS.md",
    ROOT / "docs" / "DEVELOPMENT.md",
    ROOT / "docs" / "UPSTREAM.md",
]


def iter_documents() -> list[Path]:
    documents = [path for path in FORK_DOCUMENTS if path.is_file()]
    docs_dir = ROOT / "docs"
    if docs_dir.is_dir():
        for p in sorted(docs_dir.glob("*.md")):
            if p not in documents and p.name not in SKIP_NAMES:
                documents.append(p)
    return [path for path in documents if path.name not in SKIP_NAMES]


def _destination(raw: str) -> str:
    """The link destination of a `(...)` body, without an optional title.

    `[a](FORK.md "Fork notes")` and `[a](<FORK.md> 'Fork notes')` both point at FORK.md; the
    title is not part of the file name.
    """
    body = raw.strip()
    if body.startswith("<"):
        end = body.find(">")
        return body[1:end] if end != -1 else body[1:]
    parts = body.split(None, 1)
    return parts[0] if parts else ""


def _check_casing(base: Path, rel_str: str) -> tuple[bool, str | None]:
    """Check whether every component of rel_str exists with exact casing.

    On Windows, the filesystem is case-insensitive, so `path.exists()` succeeds for `fork.md`
    even if the file is named `FORK.md` on disk. In GitHub or Linux, however, the link would 404.
    Returns (True, actual_path) if every part matches exactly, (False, actual_path) if the target
    exists but has case mismatch, or (False, None) if the target does not exist.
    """
    current = base.resolve()
    rel_path = Path(rel_str)
    if not rel_path.parts:
        return (base / rel_str).resolve().exists(), ""
    actual_parts: list[str] = []
    has_mismatch = False
    for part in rel_path.parts:
        if part in (".", ""):
            continue
        if part == "..":
            actual_parts.append("..")
            current = current.parent
            continue
        try:
            entries = [e.name for e in os.scandir(current)]
        except OSError:
            return False, None
        if part in entries:
            actual_parts.append(part)
            current = current / part
        else:
            lower_map = {e.lower(): e for e in entries}
            if part.lower() in lower_map:
                has_mismatch = True
                actual_name = lower_map[part.lower()]
                actual_parts.append(actual_name)
                current = current / actual_name
            else:
                return False, None
    actual = "/".join(actual_parts)
    return (not has_mismatch), actual


def _missing_relative(path: Path, target: str) -> str | None:
    target = _destination(target)
    if not target or target.startswith(SKIP_PREFIXES):
        return None
    file_part = unquote(target.split("#", 1)[0])
    if not file_part:
        return None
    resolved = (path.parent / file_part).resolve()
    if not resolved.is_relative_to(ROOT):
        return f"{target} → 逃出 repo 根目錄"
    match, actual = _check_casing(path.parent, file_part)
    if match:
        return None
    if actual is not None:
        return f"{target} → 大小寫不符（磁碟上為 {actual}）"
    try:
        shown = resolved.relative_to(ROOT)
    except ValueError:
        shown = resolved
    return f"{target} → 找不到 {shown}"


def _without_code(text: str) -> str:
    """Drop fenced code blocks and inline code spans: links shown there are examples."""
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        opener = FENCE_PATTERN.match(line)
        if fence is not None:
            closes = (
                opener is not None
                and opener.group(1)[0] == fence[0]
                and len(opener.group(1)) >= len(fence)
                and set(line.strip()) == {fence[0]}
            )
            if closes:
                fence = None
            continue
        if opener:
            fence = opener.group(1)  # an unclosed fence runs to the end of the document
            continue
        kept.append(line)
    return CODE_SPAN_PATTERN.sub(" ", "".join(kept))


def check_document(path: Path) -> list[str]:
    problems: list[str] = []
    text = _without_code(path.read_text(encoding="utf-8"))
    for pattern in (LINK_PATTERN, IMAGE_PATTERN, HTML_SRC_PATTERN):
        for match in pattern.finditer(text):
            missing = _missing_relative(path, match.group(1))
            if missing:
                problems.append(missing)
    return problems


def main() -> int:
    documents = iter_documents()
    if not documents:
        print("找不到任何 fork overlay Markdown 檔")
        return 1

    failures = 0
    for path in documents:
        problems = check_document(path)
        rel = path.relative_to(ROOT)
        if problems:
            failures += 1
            for problem in problems:
                print(f"FAIL {rel}: {problem}")
        else:
            print(f"OK   {rel}")

    print(f"\n共 {len(documents)} 份 overlay 文件，{failures} 份有缺檔。")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
