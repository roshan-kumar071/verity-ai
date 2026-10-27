
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from verity.config import get_tavily_api_key


TAVILY_SEARCH_URL = "https://api.tavily.com/search"

TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "dclid",
    "msclkid",
}


def normalize_url(url: str) -> str:
    """Normalize a URL for duplicate detection."""
    url = url.strip()

    if not url:
        return ""

    try:
        parts = urlsplit(url)
        hostname = (parts.hostname or "").lower()

        if not parts.scheme or not hostname:
            return url

        scheme = parts.scheme.lower()
        port = parts.port

        if port and not (
            (scheme == "http" and port == 80)
            or (scheme == "https" and port == 443)
        ):
            hostname = f"{hostname}:{port}"

        path = parts.path.rstrip("/") or "/"

        query_params = [
            (key, value)
            for key, value in parse_qsl(
                parts.query, keep_blank_values=True
            )
            if not key.lower().startswith("utm_")
            and key.lower() not in TRACKING_PARAMS
        ]

        query_params.sort()
        query = urlencode(query_params)

        return urlunsplit(
            (scheme, hostname, path, query, "")
        )

    except ValueError:
        return url


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web and return normalized, deduplicated results."""
    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    response = requests.post(
        TAVILY_SEARCH_URL,
        headers={
            "Authorization": f"Bearer {get_tavily_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    results = []
    seen_urls = set()

    for item in data.get("results", []):
        source_url = item.get("url", "").strip()
        normalized_url = normalize_url(source_url)

        # Keep the first result for each normalized URL.
        if normalized_url and normalized_url in seen_urls:
            continue

        if normalized_url:
            seen_urls.add(normalized_url)

        results.append(
            {
                "title": item.get("title", ""),
                "url": source_url,
                "content": item.get("content", ""),
                "score": item.get("score"),
            }
        )

    return results
