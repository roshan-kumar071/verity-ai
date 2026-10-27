from verity.processing import clean_source_text, process_sources

def test_clean_source_text_removes_extra_whitespace():
    text = "  Remote work   can improve\n\nproductivity.  "

    result = clean_source_text(text)

    assert result == "Remote work can improve productivity."


def test_clean_source_text_handles_empty_text():
    assert clean_source_text("") == ""
    assert clean_source_text("   ") == ""


def test_process_sources_cleans_and_preserves_source_details():
    sources = [
        {
            "title": "  Example   Source ",
            "url": " https://example.com/article ",
            "content": " Some   useful\n information. ",
            "score": 0.91,
        }
    ]

    result = process_sources(sources)

    assert len(result) == 1
    assert result[0]["title"] == "Example Source"
    assert result[0]["url"] == "https://example.com/article"
    assert result[0]["content"] == "Some useful information."
    assert result[0]["score"] == 0.91


def test_process_sources_handles_missing_fields():
    result = process_sources([{}])

    assert result == [
        {
            "title": "",
            "url": "",
            "content": "",
            "score": None,
        }
    ]
