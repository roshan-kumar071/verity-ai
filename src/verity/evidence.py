import re

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "being", "to", "of", "in", "on", "at", "for", "and", "or",
    "but", "with", "by", "from", "that", "this", "it", "as",
    "than", "into", "can", "could", "may", "might", "does",
    "do", "did", "not", "no", "often", "more", "less",
}


def get_keywords(text: str) -> set[str]:
    """Extract meaningful words for a basic text comparison."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.casefold())
    return {word for word in words if word not in STOP_WORDS}


def split_evidence_sentences(text: str) -> list[str]:
    """Split source text into individual sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

def has_subject_mismatch(claim: str, sentence: str) -> bool:
    """Detect a few known cases where the main topic differs."""
    claim_lower = claim.casefold()
    sentence_lower = sentence.casefold()

    subject_groups = [
        {"remote work", "working remotely", "work from home"},
        {"office lighting", "lighting", "office light"},
    ]

    claim_groups = {
        index
        for index, group in enumerate(subject_groups)
        if any(term in claim_lower for term in group)
    }
    sentence_groups = {
        index
        for index, group in enumerate(subject_groups)
        if any(term in sentence_lower for term in group)
    }

    return bool(claim_groups and sentence_groups and claim_groups.isdisjoint(sentence_groups))


def has_number_mismatch(claim: str, sentence: str) -> bool:
    """Reject evidence when claim and sentence contain different numbers."""
    claim_numbers = re.findall(r"\b\d+(?:\.\d+)?%?\b", claim)
    sentence_numbers = re.findall(r"\b\d+(?:\.\d+)?%?\b", sentence)

    return bool(claim_numbers and sentence_numbers and claim_numbers != sentence_numbers)

def has_uncovered_claim_parts(claim: str, sentence: str) -> bool:
    """Detect when a claim has multiple improvement outcomes but evidence covers only one."""
    claim_lower = claim.casefold()
    sentence_lower = sentence.casefold()

    outcome_groups = [
        {"productivity", "productive"},
        {"satisfaction", "satisfied"},
        {"performance"},
        {"health"},
        {"sleep"},
        {"learning", "outcomes"},
        {"speed"},
    ]

    claim_outcomes = {
        index
        for index, group in enumerate(outcome_groups)
        if any(term in claim_lower for term in group)
    }
    sentence_outcomes = {
        index
        for index, group in enumerate(outcome_groups)
        if any(term in sentence_lower for term in group)
    }

    return bool(claim_outcomes and not claim_outcomes.issubset(sentence_outcomes))

def compare_evidence(claim: str, sources: list[dict]) -> dict:
    """Classify source text as preliminary evidence for a claim."""
    supporting = []
    contradicting = []
    insufficient = []

    for source in sources:
        content = source.get("content", "")

        if not isinstance(content, str) or not content.strip():
            continue

        item = {
            "source_title": source.get("title", ""),
            "source_url": source.get("url", ""),
            "text": content,
            "keyword_overlap": round(
                len(get_keywords(claim) & get_keywords(content))
                / max(len(get_keywords(claim)), 1),
                2,
            ),
        }

        classification = classify_evidence(claim, content)

        if classification == "supporting":
            supporting.append(item)
        elif classification == "contradicting":
            contradicting.append(item)
        else:
            insufficient.append(item)

    return {
        "claim": claim,
        "supporting": supporting,
        "contradicting": contradicting,
        "insufficient": insufficient,
    }


def classify_evidence(claim: str, source_text: str) -> str:
    """Conservatively classify evidence sentence by sentence."""
    claim_words = get_keywords(claim)

    if not claim_words or not source_text.strip():
        return "insufficient"

    positive_words = {
        "improve", "improves", "improved", "increase", "increases",
        "increased", "boost", "boosts", "higher", "better",
    }
    negative_words = {
        "reduce", "reduces", "reduced", "decrease", "decreases",
        "decreased", "lower", "worse", "harm", "harms",
    }

    negation_patterns = [
        r"\bnot\b", r"\bno\b", r"\bnever\b", r"\bneither\b",
        r"\bwithout\b", r"\bn't\b", r"\bfails?\s+to\b",
    ]

    uncertainty_patterns = [
        r"\bmay\b", r"\bmight\b", r"\bcould\b",
        r"\bpossibly\b", r"\bperhaps\b", r"\buncertain\b",
        r"\bdepends\b", r"\bhowever\b", r"\bbut\b",
        r"\bmixed results\b", r"\bresults vary\b",
    ]

    claim_positive = bool(claim_words & positive_words)
    claim_negative = bool(claim_words & negative_words)

    if claim_positive == claim_negative:
        return "insufficient"

    results = []

    for sentence in split_evidence_sentences(source_text):
        if has_number_mismatch(claim, sentence):
            results.append("insufficient")
            continue
        if has_uncovered_claim_parts(claim, sentence):
            results.append("insufficient")
            continue
        if has_subject_mismatch(claim, sentence):
            results.append("insufficient")
            continue
        sentence_lower = sentence.casefold()
        sentence_words = get_keywords(sentence)

        if not sentence_words:
            continue

        
        overlap = claim_words & sentence_words
        relevance = len(overlap) / len(claim_words)

        if relevance < 0.5:
            continue

        # Reject evidence with a different main subject.
        claim_subjects = claim_words - positive_words - negative_words
        sentence_subjects = sentence_words - positive_words - negative_words

        if claim_subjects and sentence_subjects:
            subject_overlap = len(
                claim_subjects & sentence_subjects
            ) / len(claim_subjects)

            if subject_overlap < 0.5:
                continue

        if any(re.search(p, sentence_lower) for p in negation_patterns):
            results.append("insufficient")
            continue

        if any(re.search(p, sentence_lower) for p in uncertainty_patterns):
            results.append("insufficient")
            continue

        sentence_positive = bool(sentence_words & positive_words)
        sentence_negative = bool(sentence_words & negative_words)

        if sentence_positive == sentence_negative:
            results.append("insufficient")
        elif claim_positive and sentence_positive:
            results.append("supporting")
        elif claim_negative and sentence_negative:
            results.append("supporting")
        else:
            results.append("contradicting")

    decisive_results = {
        result for result in results
        if result in {"supporting", "contradicting"}
    }

    if len(decisive_results) != 1:
        return "insufficient"

    if "insufficient" in results:
        return "insufficient"

    return next(iter(decisive_results))
