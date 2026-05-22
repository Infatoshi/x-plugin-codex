# X for Codex

Codex plugin that exposes X/Twitter actions as MCP tools by reusing the
[`x-cli`](https://github.com/INFATOSHI/x-cli) Python API client.

This plugin intentionally stays thin:

- It does not reimplement X auth.
- It uses the `x_cli` package API directly.
- It keeps public write actions explicit in the tool names.

## Requirements

- `uv`
- Working X credentials, for example `~/.config/x-cli/.env`

On Elliot's MacBook, this is already set up as:

```bash
~/.config/x-cli/.env
```

## Tools

Read tools:

- `x_user_get`
- `x_user_timeline`
- `x_tweet_get`
- `x_tweet_search`
- `x_me_mentions`

Write tools:

- `x_tweet_post`
- `x_tweet_reply`
- `x_tweet_quote`
- `x_like_tweet`
- `x_retweet`

## Development

```bash
uv sync
uv run pytest
uv run ruff check . --fix
uv run x-plugin-codex-mcp
```
