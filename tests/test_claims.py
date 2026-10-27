from verity.claims import extract_claims

def test_extract_claims_preserves_source_details():
    sources = [
        {
            "title": "Remote Work Study",
            "url": "https://example.com/study",
            "content": (
                "Remote work can improve employee productivity. "
                "Some employees report feeling isolated."
            ),
        }
    ]

    claims = extract_claims(sources)

    assert len(claims) == 2
    assert claims[0]["claim"] == (
        "Remote work can improve employee productivity."
    )
    assert claims[0]["source_title"] == "Remote Work Study"
    assert claims[0]["source_url"] == "https://example.com/study"


def test_extract_claims_skips_questions_and_short_fragments():
    sources = [
        {
            "title": "Example",
            "url": "https://example.com",
            "content": "Is this true? Short text. Remote work can improve employee productivity.",
        }
    ]

    claims = extract_claims(sources)

    assert len(claims) == 1
    assert claims[0]["claim"] == (
        "Remote work can improve employee productivity."
    )


def test_extract_claims_removes_duplicate_sentences():
    sources = [
        {
            "title": "Source A",
            "url": "https://example.com/a",
            "content": (
                "Remote work can improve employee productivity. "
                "Remote work can improve employee productivity."
            ),
        }
    ]

    claims = extract_claims(sources)

    assert len(claims) == 1


def test_extract_claims_handles_empty_content():
    sources = [
        {"title": "Empty", "url": "https://example.com", "content": ""},
        {"title": "Missing content", "url": "https://example.org"},
    ]

    assert extract_claims(sources) == []


def test_extract_claims_preserves_common_abbreviations():
    sources = [
        {
            "title": "Productivity Study",
            "url": "https://example.com/study",
            "content": (
                "Research from the U.S. Bureau of Labor Statistics "
                "highlights productivity differences. "
                "Remote vs. in-person work can produce different outcomes."
            ),
        }
    ]

    claims = extract_claims(sources)

    assert len(claims) == 2
    assert "U.S. Bureau of Labor Statistics" in claims[0]["claim"]
    assert claims[1]["claim"].startswith("Remote vs. in-person work")


def test_extract_claims_skips_incomplete_search_snippets():
    sources = [
        {
            "title": "Example",
            "url": "https://example.com",
            "content": (
                "Remote workers can improve productivity. "
                "Some studies report benefits [...] other studies show mixed results."
            ),
        }
    ]

    claims = extract_claims(sources)

    assert len(claims) == 1
    assert claims[0]["claim"] == (
        "Remote workers can improve productivity."
    )

def test_extract_claims_ignores_obvious_page_noise():
    sources = [
        {
            "title": "Example page",
            "url": "https://example.com",
            "content": (
                "Remote work can improve employee productivity. "
                "Delivered to your inbox! "
                "Each of the 25 puzzle words start with a different letter. "
                "A recent paper from Jose Maria Barrero, Nicholas Bloom, and Steven J."
            ),
        }
    ]

    claims = extract_claims(sources)
    extracted_text = [item["claim"] for item in claims]

    assert "Remote work can improve employee productivity." in extracted_text
    assert "Delivered to your inbox!" not in extracted_text
    assert not any("puzzle words" in claim for claim in extracted_text)
    assert not any("Steven J." in claim for claim in extracted_text)


def test_extract_claims_filters_sourdough_and_employee_hiking_noise():
    sources = [
        {
            "title": "Remote Work Article",
            "url": "https://example.com/remote-work",
            "content": (
                "Remote work can improve employee productivity. "
                "Sourdough bread baking has become popular. "
                "One of our employees takes hikes every Wednesday."
            ),
        }
    ]

    claims = extract_claims(sources)
    extracted_text = [item["claim"] for item in claims]

    assert "Remote work can improve employee productivity." in extracted_text
    assert not any("Sourdough bread baking" in claim for claim in extracted_text)
    assert not any("takes hikes" in claim for claim in extracted_text)


def test_extract_claims_preserves_relevant_remote_work_context():
    sources = [
        {
            "title": "Remote Work Research",
            "url": "https://example.com/research",
            "content": (
                "Remote work offers employees more flexibility. "
                "Long commutes can reduce the time available for focused work. "
                "Clear communication can improve team productivity."
            ),
        }
    ]

    claims = extract_claims(sources)
    extracted_text = [item["claim"] for item in claims]

    assert len(extracted_text) == 3
    assert any("more flexibility" in claim for claim in extracted_text)
    assert any("Long commutes" in claim for claim in extracted_text)
    assert any("team productivity" in claim for claim in extracted_text)


from verity.claims import is_relevant_to_question


def test_relevance_filter_keeps_remote_work_productivity_claims():
    question = (
        "Does remote work improve employee productivity "
        "compared to working from the office?"
    )

    assert is_relevant_to_question(
        "Remote work can improve employee productivity.",
        question,
    )


def test_relevance_filter_rejects_unrelated_baking_content():
    question = (
        "Does remote work improve employee productivity "
        "compared to working from the office?"
    )

    assert not is_relevant_to_question(
        "Sourdough bread baking has become popular.",
        question,
    )


def test_extract_claims_applies_question_relevance_filter():
    sources = [
        {
            "title": "Remote Work Article",
            "url": "https://example.com",
            "content": (
                "Remote work can improve employee productivity. "
                "Sourdough bread baking has become popular."
            ),
        }
    ]

    claims = extract_claims(
        sources,
        "Does remote work improve employee productivity?",
    )

    extracted_text = [item["claim"] for item in claims]

    assert "Remote work can improve employee productivity." in extracted_text
    assert not any("Sourdough" in claim for claim in extracted_text)


def test_extract_claims_rejects_incomplete_trailing_words():
    sources = [
        {
            "title": "Example",
            "url": "https://example.com",
            "content": (
                "Remote work can improve employee productivity. "
                "This comparative analysis fosters informed decision-making whether"
            ),
        }
    ]

    claims = extract_claims(sources)
    extracted_text = [item["claim"] for item in claims]

    assert "Remote work can improve employee productivity." in extracted_text
    assert not any(
        claim.endswith("whether")
        for claim in extracted_text
    )


def test_relevance_filter_rejects_weak_keyword_overlap():
    question = (
        "Does remote work improve employee productivity "
        "compared to working from the office?"
    )

    assert not is_relevant_to_question(
        "Office buildings contain several meeting rooms.",
        question,
    )


def test_relevance_filter_keeps_relevant_claim_without_exact_question_words():
    question = (
        "Does remote work improve employee productivity "
        "compared to working from the office?"
    )

    assert is_relevant_to_question(
        "Working from home can help staff finish more tasks.",
        question,
    )


def test_split_sentences_separates_sentences_without_extra_spaces():
    from verity.claims import split_sentences

    text = (
        "These interruptions reduce deep work time. "
        "Studies indicate remote workers spend less time being unproductive."
    )

    sentences = split_sentences(text)

    assert len(sentences) == 2
    assert sentences[0] == "These interruptions reduce deep work time."
    assert sentences[1] == (
        "Studies indicate remote workers spend less time being unproductive."
    )


def test_split_sentences_separates_merged_productivity_claims():
    from verity.claims import split_sentences

    text = (
        "These interruptions reduce deep work time, affecting much of the productivity "
        "Studies indicate that remote workers spend less time being unproductive "
        "compared with office employees, largely due to reduced distractions."
    )

    sentences = split_sentences(text)

    assert len(sentences) == 2
    assert sentences[0].endswith("productivity")
    assert sentences[1].startswith("Studies indicate")
