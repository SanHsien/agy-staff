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
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x", encoding="utf-8")
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


class CodeIsNotALinkTests(unittest.TestCase):
    def test_example_links_in_fenced_code_are_not_checked(self) -> None:
        # A doc that *shows* link syntax inside a code fence made the gate fail on the
        # example path, which is not meant to exist.
        fenced = "Use this:\n\n```md\n[guide](docs/NEW_GUIDE.md)\n![x](img/none.png)\n```\n"
        self.assertEqual(problems_for(fenced), [])
        tilde = "~~~\n[guide](docs/NEW_GUIDE.md)\n~~~\n"
        self.assertEqual(problems_for(tilde), [])

    def test_example_links_in_inline_code_are_not_checked(self) -> None:
        self.assertEqual(problems_for("Write `[guide](docs/NEW_GUIDE.md)` like so.\n"), [])

    def test_real_links_around_code_are_still_checked(self) -> None:
        text = "[a](BEFORE.md)\n\n```\n[x](IN_FENCE.md)\n```\n\n[b](AFTER.md) and `[c](IN_SPAN.md)`\n"
        found = problems_for(text)
        self.assertEqual(len(found), 2, found)
        self.assertIn("BEFORE.md", found[0])
        self.assertIn("AFTER.md", found[1])

    def test_an_unclosed_fence_hides_only_the_rest_of_the_document(self) -> None:
        text = "[a](BEFORE.md)\n\n```\n[x](IN_FENCE.md)\n"
        found = problems_for(text)
        self.assertEqual(len(found), 1, found)
        self.assertIn("BEFORE.md", found[0])


class CaseSensitivityTests(unittest.TestCase):
    def test_case_mismatch_is_reported(self) -> None:
        # On Windows (case-insensitive filesystem), a link pointing to `fork.md` when the
        # file is named `FORK.md` would previously pass the existence check but fail on GitHub.
        found = problems_for("See [fork](fork.md).\n")
        self.assertEqual(len(found), 1)
        self.assertIn("fork.md", found[0])
        self.assertIn("大小寫不符", found[0])

    def test_exact_case_passes(self) -> None:
        self.assertEqual(problems_for("See [fork](FORK.md).\n"), [])

    def test_nested_path_case_mismatch_is_reported(self) -> None:
        found = problems_for(
            "See [decisions](docs/decisions.md).\n",
            existing=("FORK.md", "docs/DECISIONS.md"),
        )
        self.assertEqual(len(found), 1)
        self.assertIn("docs/decisions.md", found[0])
        self.assertIn("大小寫不符", found[0])


if __name__ == "__main__":
    unittest.main()
