"""The fork's own instructions must name the branch this fork actually uses."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def default_branch() -> str:
    # ci.yml runs on pushes to the fork's default branch; the rename from master to main is
    # what made the documented `--base master` stale.
    match = re.search(r"push:\s*\n\s*branches:\s*\[([\w\-/]+)\]", read(".github/workflows/ci.yml"))
    assert match, "ci.yml no longer declares a push branch"
    return match.group(1)


class DocumentedBranchTests(unittest.TestCase):
    def test_pr_base_in_instructions_is_the_default_branch(self) -> None:
        # `gh pr create --base master` fails ("base branch ... not found") on a repo whose
        # default branch is main, so the copy-paste command in the docs did not work.
        branch = default_branch()
        for doc in ("FORK.md", "CONTRIBUTING.md", ".cursor/rules/no-upstream-pr.mdc"):
            bases = re.findall(r"--base\s+(\S+)", read(doc))
            self.assertTrue(bases, f"{doc} documents no --base")
            self.assertEqual(set(bases), {branch}, doc)

    def test_branch_guards_and_support_policy_name_the_default_branch(self) -> None:
        branch = default_branch()
        rule = read(".cursor/rules/no-upstream-pr.mdc")
        self.assertEqual(re.findall(r"force-push\s+`(\w+)`", rule), [branch])
        self.assertIn(f"合併回 {branch}", rule)
        self.assertRegex(read("SECURITY.md"), rf"`{branch}` 分支")
        self.assertIn(f"合併回 `{branch}`", read("docs/UPSTREAM.md"))


if __name__ == "__main__":
    unittest.main()
