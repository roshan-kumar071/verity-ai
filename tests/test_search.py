
import pytest

from verity.search import normalize_url, search_web


def test_empty_query_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        search_web("   ")


@pytest.mark.parametrize("count", [0, 11, -1])
def test_invalid_result_count_is_rejected(count):
    with pytest.raises(ValueError, match="between 1 and 10"):
        search_web("AI research", max_results=count)



def test_search_results_are_normalized(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "title": "Example source",
                        "url": "https://example.com/article",
                        "content": "Example evidence text",
                        "score": 0.91,
                    }
                ]
            }

    def fake_post(url, headers, json, timeout):
        assert url == "https://api.tavily.com/search"
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"
        assert "api_key" not in json
        assert json["query"] == "AI research"
        assert json["max_results"] == 3
        assert json["search_depth"] == "basic"
        assert timeout == 30
        return FakeResponse()

    monkeypatch.setattr("verity.search.requests.post", fake_post)

    results = search_web("AI research", max_results=3)

    assert len(results) == 1
    assert results[0]["title"] == "Example source"
    assert results[0]["url"] == "https://example.com/article"
    assert results[0]["content"] == "Example evidence text"
    assert results[0]["score"] == 0.91


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://Example.com/article/?utm_source=newsletter",
            "https://example.com/article",
        ),
        (
            "https://example.com/article?fbclid=tracking123",
            "https://example.com/article",
        ),
        (
            "https://example.com/article?category=research",
            "https://example.com/article?category=research",
        ),
        (
            "https://example.com/another-article",
            "https://example.com/another-article",
        ),
        ("", ""),
    ],
)
def test_normalize_url(url, expected):
    assert normalize_url(url) == expected


def test_search_results_remove_duplicate_normalized_urls(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "title": "Original article",
                        "url": "https://example.com/article",
                        "content": "First result",
                        "score": 0.95,
                    },
                    {
                        "title": "Duplicate article",
                        "url": (
                            "https://EXAMPLE.com/article/"
                            "?utm_source=newsletter"
                        ),
                        "content": "Duplicate result",
                        "score": 0.80,
                    },
                    {
                        "title": "Different article",
                        "url": "https://example.com/another-article",
                        "content": "Different result",
                        "score": 0.75,
                    },
                ]
            }

    monkeypatch.setattr(
        "verity.search.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    results = search_web("AI research")

    assert len(results) == 2
    assert results[0]["title"] == "Original article"
    assert results[0]["content"] == "First result"
    assert results[1]["title"] == "Different article"


def test_same_title_with_different_urls_are_preserved(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "title": "Remote Work and Productivity",
                        "url": "https://example.com/article-a",
                        "content": "Study A findings",
                        "score": 0.95,
                    },
                    {
                        "title": "Remote Work and Productivity",
                        "url": "https://example.com/article-b",
                        "content": "Study B findings",
                        "score": 0.85,
                    },
                ]
            }

    monkeypatch.setattr(
        "verity.search.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    results = search_web("remote work productivity")

    assert len(results) == 2
    assert results[0]["url"] == "https://example.com/article-a"
    assert results[1]["url"] == "https://example.com/article-b"
