"""Contract tests for tools/check_links.py (offline, temp directory only)."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("check_links", ROOT / "tools" / "check_links.py")
assert _SPEC is not None and _SPEC.loader is not None
links = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = links
_SPEC.loader.exec_module(links)


def problems_for(text: str, existing: tuple[str, ...] = ("FORK.md",)) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        for name in existing:
            (root / name).write_text("x", encoding="utf-8")
        doc = root / "README.md"
        doc.write_text(text, encoding="utf-8")
        with mock.patch.object(links, "ROOT", root):
            return links.check_document(doc)


class LinkTargetTests(unittest.TestCase):
    def test_a_link_title_is_not_part_of_the_file_name(self) -> None:
        # `[a](FORK.md "Fork notes")` is a valid CommonMark link to FORK.md; the checker
        # looked for a file literally named `FORK.md "Fork notes"` and failed the gate.
        self.assertEqual(problems_for('See [fork](FORK.md "Fork notes").\n'), [])
        self.assertEqual(problems_for("See [fork](FORK.md 'Fork notes').\n"), [])
        self.assertEqual(problems_for('See [fork](<FORK.md> "Fork notes").\n'), [])

    def test_a_missing_target_with_a_title_is_still_reported(self) -> None:
        found = problems_for('See [gone](MISSING.md "Gone").\n')
        self.assertEqual(len(found), 1)
        self.assertIn("MISSING.md", found[0])
        self.assertNotIn("Gone", found[0])


if __name__ == "__main__":
    unittest.main()
