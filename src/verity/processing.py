
import re


def clean_source_text(text: str) -> str:
    """Clean unnecessary whitespace from source text."""
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def process_sources(sources: list[dict]) -> list[dict]:
    """Clean and standardize web search results."""
    processed = []

    for source in sources:
        content = clean_source_text(source.get("content", ""))

        processed.append(
            {
                "title": clean_source_text(source.get("title", "")),
                "url": source.get("url", "").strip(),
                "content": content,
                "score": source.get("score"),
            }
        )

    return processed
