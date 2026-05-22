"""MCP server that wraps the x_cli Python API client."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from x_cli.api import XApiClient
from x_cli.auth import load_credentials
from x_cli.utils import parse_tweet_id, strip_at

mcp = FastMCP("x-plugin-codex")


def _with_client(method: str, *args: Any, **kwargs: Any) -> Any:
    """Load credentials, call one XApiClient method, and close the HTTP client."""
    client = XApiClient(load_credentials())
    try:
        return getattr(client, method)(*args, **kwargs)
    finally:
        client.close()


@mcp.tool()
def x_user_get(username: str) -> Any:
    """Look up an X user profile by username."""
    return _with_client("get_user", strip_at(username))


@mcp.tool()
def x_user_timeline(username: str, max_results: int = 10) -> Any:
    """Fetch recent posts from an X user's timeline."""
    user = _with_client("get_user", strip_at(username))
    return _with_client("get_timeline", user["data"]["id"], max_results)


@mcp.tool()
def x_tweet_get(id_or_url: str) -> Any:
    """Fetch one X post by tweet ID or URL."""
    return _with_client("get_tweet", parse_tweet_id(id_or_url))


@mcp.tool()
def x_tweet_search(query: str, max_results: int = 10) -> Any:
    """Search recent X posts."""
    return _with_client("search_tweets", query, max_results)


@mcp.tool()
def x_me_mentions(max_results: int = 10) -> Any:
    """Fetch recent mentions for the authenticated X account."""
    return _with_client("get_mentions", max_results)


@mcp.tool()
def x_tweet_post(text: str) -> Any:
    """Publicly post a new tweet from the authenticated X account."""
    return _with_client("post_tweet", text)


@mcp.tool()
def x_tweet_reply(id_or_url: str, text: str) -> Any:
    """Publicly reply to an X post from the authenticated X account."""
    return _with_client("post_tweet", text, reply_to=parse_tweet_id(id_or_url))


@mcp.tool()
def x_tweet_quote(id_or_url: str, text: str) -> Any:
    """Publicly quote an X post from the authenticated X account."""
    return _with_client("post_tweet", text, quote_tweet_id=parse_tweet_id(id_or_url))


@mcp.tool()
def x_like_tweet(id_or_url: str) -> Any:
    """Like an X post from the authenticated X account."""
    return _with_client("like_tweet", parse_tweet_id(id_or_url))


@mcp.tool()
def x_retweet(id_or_url: str) -> Any:
    """Retweet an X post from the authenticated X account."""
    return _with_client("retweet", parse_tweet_id(id_or_url))


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
