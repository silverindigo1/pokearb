"""The command line accepts what the workflow actually sends."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from pokearb import cli

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "daily.yml"


@pytest.mark.parametrize(
    "argv",
    [
        ["build", "--verbose"],
        ["--verbose", "build"],
        ["-v", "build", "--only", "tcgviert"],
        ["build", "--only", "tcgviert", "-v"],
        ["build"],
    ],
)
def test_verbose_before_or_after_the_command(argv, monkeypatch):
    seen = {}
    monkeypatch.setattr(cli, "cmd_build", lambda args: seen.setdefault("args", args) and 0)
    assert cli.main(argv) == 0
    assert seen["args"].command == "build"


def test_the_workflow_command_parses(monkeypatch):
    """Guard against the exact failure of the first GitHub run (23-09-2026)."""
    text = WORKFLOW.read_text("utf-8")
    line = re.search(r"python -m pokearb\.cli ([^\n\\]+)", text).group(1).split()
    seen = {}
    monkeypatch.setattr(cli, "cmd_build", lambda args: seen.setdefault("args", args) and 0)
    assert cli.main(line) == 0
    assert seen["args"].command == "build"


def test_a_slow_shop_gets_a_second_chance(monkeypatch):
    """A read timeout is retried with a longer timeout instead of losing the shop."""
    import requests

    from pokearb import http

    session = http.PoliteSession()
    monkeypatch.setattr(http, "TIMEOUT_BACKOFF", 0)
    monkeypatch.setattr(session, "_wait", lambda host: None)
    seen = []

    class Ok:
        status_code = 200
        headers = {}

        def raise_for_status(self):
            return None

    def fake_get(url, headers=None, timeout=None, **kwargs):
        seen.append(timeout)
        if len(seen) == 1:
            raise requests.ReadTimeout("slow")
        return Ok()

    monkeypatch.setattr(session.session, "get", fake_get)
    assert session.get("https://example.test/x").status_code == 200
    assert len(seen) == 2 and seen[1] > seen[0]
