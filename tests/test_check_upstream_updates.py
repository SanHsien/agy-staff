"""Contract tests for tools/check_upstream_updates.py (offline: `gh` and `git` are injected)."""

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "check_upstream_updates", ROOT / "tools" / "check_upstream_updates.py"
)
assert _SPEC is not None and _SPEC.loader is not None
upstream = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = upstream
_SPEC.loader.exec_module(upstream)

BASELINE = {"repo": "https://github.com/owner/name.git", "reviewed_pr_through": 0}


def fake_gh(total: int):
    """A `gh <kind> list` stand-in that, like the real one, returns the newest `--limit` items."""

    def run(args, **_kwargs):
        limit = int(args[args.index("--limit") + 1])
        newest_first = [{"number": n, "title": f"item {n}"} for n in range(total, 0, -1)]
        return subprocess.CompletedProcess(args, 0, json.dumps(newest_first[:limit]), "")

    return run


class TicketEnumerationTests(unittest.TestCase):


    def test_unreadable_gh_is_not_checked_rather_than_empty(self) -> None:
        failed = subprocess.CompletedProcess([], 1, "", "boom")
        with mock.patch.object(upstream.subprocess, "run", return_value=failed):
            self.assertIsNone(upstream.collect_new_tickets(dict(BASELINE), "issue"))


if __name__ == "__main__":
    unittest.main()
