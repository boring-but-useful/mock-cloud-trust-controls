from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_link_check(project_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "check_markdown_links.py"),
            "--root",
            str(project_root),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


class CheckMarkdownLinksTests(unittest.TestCase):
    def test_accepts_valid_local_image_fragment_and_external_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            docs_dir = project_root / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
            (docs_dir / "diagram.svg").write_text("<svg/>\n", encoding="utf-8")
            (project_root / "README.md").write_text(
                "\n".join(
                    (
                        "[Guide](docs/guide.md?plain=1#guide)",
                        "![Diagram](docs/diagram.svg)",
                        "[Section](#local-section)",
                        "[External](https://example.com)",
                    )
                ),
                encoding="utf-8",
            )

            result = run_link_check(project_root)

            self.assertEqual(result.returncode, 0)
            self.assertIn("Validated local links in 2 Markdown files", result.stdout)

    def test_reports_missing_local_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            (project_root / "README.md").write_text(
                "[Missing](docs/missing.md)\n",
                encoding="utf-8",
            )

            result = run_link_check(project_root)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "README.md:1: missing local target 'docs/missing.md'",
                result.stdout,
            )

    def test_rejects_target_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / "README.md").write_text(
                "[Outside](../outside.md)\n",
                encoding="utf-8",
            )

            result = run_link_check(project_root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("local target escapes the repository", result.stdout)

    def test_rejects_missing_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_root = Path(tmp_dir) / "missing"

            result = run_link_check(missing_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("repository root not found", result.stdout)


if __name__ == "__main__":
    unittest.main()
