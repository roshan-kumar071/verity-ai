import os


def get_tavily_api_key() -> str:
    """Return the Tavily API key from environment variables."""
    api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing. "
            "Set it in your local environment before searching."
        )

    return api_key