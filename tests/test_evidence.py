from verity.evidence import (
    classify_evidence,
    compare_evidence,
    get_keywords,
)


def test_get_keywords_removes_common_stop_words():
    keywords = get_keywords(
        "The employee productivity is improved by remote work"
    )

    assert "the" not in keywords
    assert "productivity" in keywords
    assert "remote" in keywords


def test_compare_evidence_preserves_source_details():
    sources = [
        {
            "title": "Remote Work Study",
            "url": "https://example.com/study",
            "content": "Remote work may improve employee productivity.",
        }
    ]

    result = compare_evidence(
        "Remote work improves employee productivity.",
        sources,
    )

    assert result["claim"] == (
        "Remote work improves employee productivity."
    )
    assert result["supporting"] == []
    assert result["contradicting"] == []
    assert len(result["insufficient"]) == 1
    assert result["insufficient"][0]["source_title"] == (
        "Remote Work Study"
    )
    assert result["insufficient"][0]["source_url"] == (
        "https://example.com/study"
    )


def test_compare_evidence_handles_empty_sources():
    result = compare_evidence(
        "Remote work improves employee productivity.",
        [],
    )

    assert result["supporting"] == []
    assert result["contradicting"] == []
    assert result["insufficient"] == []


def test_compare_evidence_handles_empty_claim():
    result = compare_evidence("", [])

    assert result["claim"] == ""
    assert result["supporting"] == []
    assert result["contradicting"] == []
    assert result["insufficient"] == []


def test_compare_evidence_does_not_treat_keyword_overlap_as_proof():
    sources = [
        {
            "title": "Remote Work Article",
            "url": "https://example.com/remote-work",
            "content": (
                "Remote work and employee productivity are discussed, "
                "but no conclusion is provided."
            ),
        }
    ]

    result = compare_evidence(
        "Remote work improves employee productivity.",
        sources,
    )

    assert result["supporting"] == []
    assert result["contradicting"] == []
    assert len(result["insufficient"]) == 1


def test_compare_evidence_keeps_unrelated_sources_unclassified():
    sources = [
        {
            "title": "Office Design",
            "url": "https://example.com/office",
            "content": (
                "Modern office buildings often include meeting rooms "
                "and shared spaces."
            ),
        }
    ]

    result = compare_evidence(
        "Remote work improves employee productivity.",
        sources,
    )

    assert result["supporting"] == []
    assert result["contradicting"] == []
    assert len(result["insufficient"]) == 1


def test_compare_evidence_preserves_multiple_source_records():
    sources = [
        {
            "title": "Source A",
            "url": "https://example.com/a",
            "content": "Remote work may improve employee productivity.",
        },
        {
            "title": "Source B",
            "url": "https://example.com/b",
            "content": "Remote work may affect employee productivity.",
        },
    ]

    result = compare_evidence(
        "Remote work improves employee productivity.",
        sources,
    )

    assert len(result["insufficient"]) == 2
    assert result["insufficient"][0]["source_title"] == "Source A"
    assert result["insufficient"][1]["source_title"] == "Source B"


from verity.evidence import classify_evidence


def test_classify_evidence_identifies_matching_direction():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        "Remote work improves productivity for employees.",
    )

    assert result == "supporting"


def test_classify_evidence_identifies_opposite_direction():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        "Remote work reduces employee productivity.",
    )

    assert result == "contradicting"


def test_classify_evidence_returns_insufficient_for_unrelated_text():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        "Modern office buildings have meeting rooms.",
    )

    assert result == "insufficient"


def test_classify_evidence_handles_empty_text():
    assert classify_evidence("", "Remote work improves productivity.") == (
        "insufficient"
    )
    assert classify_evidence("Remote work improves productivity.", "") == (
        "insufficient"
    )


def test_classify_evidence_treats_negation_as_insufficient():
    assert classify_evidence(
        "Remote work improves employee productivity.",
        "Remote work does not improve employee productivity.",
    ) == "insufficient"


def test_classify_evidence_treats_ambiguous_statements_as_insufficient():
    assert classify_evidence(
        "Remote work improves employee productivity.",
        "Remote work may improve employee productivity, but results vary.",
    ) == "insufficient"


def test_compare_evidence_separates_supporting_contradicting_and_insufficient():
    claim = "Remote work improves employee productivity."

    sources = [
        {
            "title": "Supporting Source",
            "url": "https://example.com/support",
            "content": "Remote work improves employee productivity.",
        },
        {
            "title": "Contradicting Source",
            "url": "https://example.com/contradict",
            "content": "Remote work reduces employee productivity.",
        },
        {
            "title": "Unclear Source",
            "url": "https://example.com/unclear",
            "content": (
                "Remote work may improve employee productivity, "
                "but results vary."
            ),
        },
    ]

    result = compare_evidence(claim, sources)

    assert len(result["supporting"]) == 1
    assert result["supporting"][0]["source_title"] == "Supporting Source"

    assert len(result["contradicting"]) == 1
    assert result["contradicting"][0]["source_title"] == "Contradicting Source"

    assert len(result["insufficient"]) == 1
    assert result["insufficient"][0]["source_title"] == "Unclear Source"


def test_classify_evidence_treats_mixed_findings_as_insufficient():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        (
            "Remote work improves productivity for focused tasks, "
            "but reduces productivity for collaborative tasks."
        ),
    )

    assert result == "insufficient"


def test_classify_evidence_treats_conflicting_findings_without_but_as_insufficient():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        (
            "Remote work improves productivity for focused tasks. "
            "Remote work reduces productivity for collaborative tasks."
        ),
    )

    assert result == "insufficient"

    
def test_classify_evidence_rejects_keyword_overlap_without_relevant_evidence():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        (
            "Remote work is common among employees. "
            "Employee productivity depends on management. "
            "The report does not measure whether remote work improves productivity."
        ),
    )

    assert result == "insufficient"


def test_classify_evidence_does_not_treat_unrelated_keyword_match_as_support():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        (
            "Remote work is popular among employees. "
            "The productivity report discusses office lighting, "
            "not the effects of remote work."
        ),
    )

    assert result == "insufficient"

def test_classify_evidence_returns_insufficient_for_mixed_sentence_findings():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        (
            "Remote work improves productivity for focused tasks. "
            "Remote work reduces productivity for collaborative tasks."
        ),
    )

    assert result == "insufficient"


def test_classify_evidence_rejects_matching_outcome_with_wrong_subject():
    result = classify_evidence(
        "Remote work improves employee productivity.",
        "Office lighting improves employee productivity.",
    )

    assert result == "insufficient"


def test_classify_evidence_does_not_confuse_different_health_topics():
    result = classify_evidence(
        "Regular exercise improves sleep quality.",
        "A balanced diet improves cardiovascular health.",
    )

    assert result == "insufficient"


def test_classify_evidence_does_not_confuse_different_technology_topics():
    result = classify_evidence(
        "Using SSDs improves computer startup speed.",
        "Adding more RAM improves multitasking performance.",
    )

    assert result == "insufficient"


def test_classify_evidence_does_not_confuse_different_education_topics():
    result = classify_evidence(
        "Smaller class sizes improve student learning outcomes.",
        "Teacher training improves classroom management.",
    )

    assert result == "insufficient"
