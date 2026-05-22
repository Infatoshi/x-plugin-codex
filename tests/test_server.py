from __future__ import annotations

import subprocess

import pytest

from x_plugin_codex import server


def test_run_x_cli_uses_json_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        assert kwargs["check"] is False
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        return subprocess.CompletedProcess(command, 0, '{"ok": true}', "")

    monkeypatch.setattr(server.subprocess, "run", fake_run)

    assert server.run_x_cli("user", "get", "openai") == {"ok": True}
    assert calls == [["x-cli", "-j", "user", "get", "openai"]]


def test_run_x_cli_honors_x_cli_path(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("X_CLI_PATH", "/tmp/x-cli")

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "{}", "")

    monkeypatch.setattr(server.subprocess, "run", fake_run)

    assert server.run_x_cli("tweet", "get", "123") == {}
    assert calls[0][0] == "/tmp/x-cli"


def test_run_x_cli_raises_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, "", "nope")

    monkeypatch.setattr(server.subprocess, "run", fake_run)

    with pytest.raises(server.XCliError, match="nope"):
        server.run_x_cli("user", "get", "openai")


def test_run_x_cli_raises_on_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, "not json", "")

    monkeypatch.setattr(server.subprocess, "run", fake_run)

    with pytest.raises(server.XCliError, match="non-JSON"):
        server.run_x_cli("user", "get", "openai")
