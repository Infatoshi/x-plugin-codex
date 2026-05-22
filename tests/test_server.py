from __future__ import annotations

from typing import Any

from x_plugin_codex import server


class FakeClient:
    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def __init__(self, creds: object) -> None:
        self.creds = creds

    def close(self) -> None:
        self.calls.append(("close", (), {}))

    def get_user(self, username: str) -> dict[str, Any]:
        self.calls.append(("get_user", (username,), {}))
        return {"data": {"id": "42", "username": username}}

    def get_timeline(self, user_id: str, max_results: int) -> dict[str, Any]:
        self.calls.append(("get_timeline", (user_id, max_results), {}))
        return {"data": [{"id": "1", "text": "hello"}]}

    def get_tweet(self, tweet_id: str) -> dict[str, Any]:
        self.calls.append(("get_tweet", (tweet_id,), {}))
        return {"data": {"id": tweet_id}}

    def search_tweets(self, query: str, max_results: int) -> dict[str, Any]:
        self.calls.append(("search_tweets", (query, max_results), {}))
        return {"data": []}

    def post_tweet(self, text: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("post_tweet", (text,), kwargs))
        return {"data": {"text": text}}


def setup_fake_client(monkeypatch):
    FakeClient.calls = []
    monkeypatch.setattr(server, "load_credentials", lambda: object())
    monkeypatch.setattr(server, "XApiClient", FakeClient)


def test_user_get_strips_at(monkeypatch) -> None:
    setup_fake_client(monkeypatch)

    assert server.x_user_get("@openai") == {"data": {"id": "42", "username": "openai"}}
    assert FakeClient.calls == [("get_user", ("openai",), {}), ("close", (), {})]


def test_user_timeline_resolves_user_id(monkeypatch) -> None:
    setup_fake_client(monkeypatch)

    assert server.x_user_timeline("openai", 7) == {"data": [{"id": "1", "text": "hello"}]}
    assert FakeClient.calls == [
        ("get_user", ("openai",), {}),
        ("close", (), {}),
        ("get_timeline", ("42", 7), {}),
        ("close", (), {}),
    ]


def test_tweet_get_parses_url(monkeypatch) -> None:
    setup_fake_client(monkeypatch)

    assert server.x_tweet_get("https://x.com/openai/status/12345") == {"data": {"id": "12345"}}


def test_write_tools_parse_target_ids(monkeypatch) -> None:
    setup_fake_client(monkeypatch)

    assert server.x_tweet_reply("https://x.com/openai/status/12345", "hi") == {
        "data": {"text": "hi"}
    }
    assert server.x_tweet_quote("12345", "look") == {"data": {"text": "look"}}
    assert FakeClient.calls == [
        ("post_tweet", ("hi",), {"reply_to": "12345"}),
        ("close", (), {}),
        ("post_tweet", ("look",), {"quote_tweet_id": "12345"}),
        ("close", (), {}),
    ]
