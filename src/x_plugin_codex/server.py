"""MCP server that wraps the local x-cli executable."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from mcp.server.fastmcp import FastMCP

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_X_CLI = "x-cli"

mcp = FastMCP("x-plugin-codex")


class XCliError(RuntimeError):
    """Raised when x-cli exits unsuccessfully or emits invalid JSON."""


def _x_cli_path() -> str:
    return os.environ.get("X_CLI_PATH", DEFAULT_X_CLI)


def run_x_cli(*args: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Any:
    """Run x-cli in JSON mode and return the decoded response."""
    command = [_x_cli_path(), "-j", *args]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise XCliError(
            "x-cli was not found on PATH. Install x-cli or set X_CLI_PATH."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise XCliError(f"x-cli timed out after {timeout} seconds: {' '.join(command)}") from exc

    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        detail = stderr or stdout or f"exit code {completed.returncode}"
        raise XCliError(f"x-cli failed: {detail}")

    output = completed.stdout.strip()
    if not output:
        return {}

    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise XCliError(f"x-cli returned non-JSON output: {output}") from exc


@mcp.tool()
def x_user_get(username: str) -> Any:
    """Look up an X user profile by username."""
    return run_x_cli("user", "get", username)


@mcp.tool()
def x_user_timeline(username: str, max_results: int = 10) -> Any:
    """Fetch recent posts from an X user's timeline."""
    return run_x_cli("user", "timeline", username, "--max", str(max_results))


@mcp.tool()
def x_tweet_get(id_or_url: str) -> Any:
    """Fetch one X post by tweet ID or URL."""
    return run_x_cli("tweet", "get", id_or_url)


@mcp.tool()
def x_tweet_search(query: str, max_results: int = 10) -> Any:
    """Search recent X posts."""
    return run_x_cli("tweet", "search", query, "--max", str(max_results))


@mcp.tool()
def x_me_mentions(max_results: int = 10) -> Any:
    """Fetch recent mentions for the authenticated X account."""
    return run_x_cli("me", "mentions", "--max", str(max_results))


@mcp.tool()
def x_tweet_post(text: str) -> Any:
    """Publicly post a new tweet from the authenticated X account."""
    return run_x_cli("tweet", "post", text)


@mcp.tool()
def x_tweet_reply(id_or_url: str, text: str) -> Any:
    """Publicly reply to an X post from the authenticated X account."""
    return run_x_cli("tweet", "reply", id_or_url, text)


@mcp.tool()
def x_tweet_quote(id_or_url: str, text: str) -> Any:
    """Publicly quote an X post from the authenticated X account."""
    return run_x_cli("tweet", "quote", id_or_url, text)


@mcp.tool()
def x_like_tweet(id_or_url: str) -> Any:
    """Like an X post from the authenticated X account."""
    return run_x_cli("like", id_or_url)


@mcp.tool()
def x_retweet(id_or_url: str) -> Any:
    """Retweet an X post from the authenticated X account."""
    return run_x_cli("retweet", id_or_url)


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
