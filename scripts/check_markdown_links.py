#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
IGNORED_DIRECTORIES = {".git", ".venv", "build", "dist", "venv"}


def markdown_files(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(
            part in IGNORED_DIRECTORIES
            for part in path.relative_to(root).parts
        )
    )


def link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split(maxsplit=1)[0]


def find_broken_links(project_root: Path) -> list[str]:
    root = project_root.resolve()
    errors: list[str] = []

    for source in markdown_files(root):
        relative_source = source.relative_to(root)
        for line_number, line in enumerate(
            source.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            for match in LINK_PATTERN.finditer(line):
                target = link_target(match.group(1))
                parsed_target = urlsplit(target)
                if not target or parsed_target.scheme or parsed_target.netloc:
                    continue

                # Fragments do not affect whether the local file exists.
                local_path = unquote(parsed_target.path)
                if not local_path:
                    continue

                candidate = (
                    root / local_path.lstrip("/")
                    if local_path.startswith("/")
                    else source.parent / local_path
                ).resolve()

                try:
                    candidate.relative_to(root)
                except ValueError:
                    errors.append(
                        f"{relative_source}:{line_number}: local target escapes "
                        f"the repository: {target!r}"
                    )
                    continue

                if not candidate.exists():
                    errors.append(
                        f"{relative_source}:{line_number}: missing local target "
                        f"{target!r}"
                    )

    return errors


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check local inline links in project Markdown files."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository root to check (default: project root).",
    )
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    if not args.root.is_dir():
        print(f"Markdown link check failed: repository root not found: {args.root}")
        return 2

    errors = find_broken_links(args.root)

    if errors:
        print("Markdown link check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    file_count = len(markdown_files(args.root.resolve()))
    print(f"Validated local links in {file_count} Markdown files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
