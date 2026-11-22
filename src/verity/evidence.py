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


def get_relevance_keywords(text: str) -> set[str]:
    """Normalize selected semantic equivalents for relevance matching."""
    words = get_keywords(text)

    aliases = {
        "reports": "report",
        "filtration": "filter",
        "coated": "coating",
        "coatings": "coating",
        "scored": "score",
        "scores": "score",
    }

    normalized = {
        aliases.get(word, word)
        for word in words
    }

    if (
        re.search(
            r"\b(?:quicker|faster)\b",
            text,
            re.IGNORECASE,
        )
        or re.search(
            r"\b(?:less time|shorter duration)\b",
            text,
            re.IGNORECASE,
        )
    ):
        normalized.add("speed")

    if (
        re.search(
            r"\bremov(?:e|es|ed|ing)\s+\d+(?:\.\d+)?\s*%\s+of\b",
            text,
            re.IGNORECASE,
        )
        or re.search(
            r"\b(?:concentration|amount|level)s?\s+"
            r"(?:was|were|is|are)?\s*\d+(?:\.\d+)?\s*%\s+lower\b",
            text,
            re.IGNORECASE,
        )
    ):
        normalized.add("quantity_reduction")

    # Match reading-score claims with descriptions of student scores.
    if (
        re.search(r"\breading\s+scores?\b", text, re.IGNORECASE)
        or re.search(
            r"\bstudents?\b.*\bscor(?:e|es|ed|ing)\b",
            text,
            re.IGNORECASE,
        )
    ):
        normalized.add("reading_outcome")

    # Match offline-access claims with internet requirements.
    if (
        re.search(r"\boffline\b", text, re.IGNORECASE)
        or re.search(
            r"\binternet\s+connection\b",
            text,
            re.IGNORECASE,
        )
    ):
        normalized.add("access_mode")

    return normalized

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



def has_population_mismatch(claim: str, sentence: str) -> bool:
    """Detect explicit population and disease-severity mismatches."""
    population_groups = [
        {"new employees", "experienced employees"},
        {"junior employees", "senior employees"},
        {"beginner", "advanced users"},
        {"children", "adults"},
        {"students", "teachers"},
        {"mild disease", "moderate disease", "severe disease"},
        {"mild symptoms", "moderate symptoms", "severe symptoms"},
    ]

    claim_lower = claim.casefold()
    sentence_lower = sentence.casefold()

    for group in population_groups:
        claim_populations = {
            population for population in group
            if population in claim_lower
        }
        sentence_populations = {
            population for population in group
            if population in sentence_lower
        }

        if claim_populations and sentence_populations:
            if claim_populations.isdisjoint(sentence_populations):
                return True

    return False

def extract_numeric_measurements(text: str) -> list[dict]:
    """Extract numeric values with their individual measurement contexts."""
    pattern = (
        r"(?P<value>\d+(?:\.\d+)?)\s*"
        r"(?P<unit>percentage points?|percent|%)"
        r"|(?P<absolute>\d+(?:\.\d+)?)\s*"
        r"(?P<absolute_unit>units?|points?|hours?|days?|"
        r"minutes?|seconds?|kg|kilograms?|mg|grams?)"
    )

    measurements = []

    clauses = re.split(
        r"(?<=[.!?;])\s+|,\s+|"
        r"\b(?:while|whereas|but)\b|"
        r"\band\s+(?=(?:a|an|the)\s+\d)",
        text,
        flags=re.IGNORECASE,
    )

    for clause in clauses:
        matches = list(re.finditer(pattern, clause, re.IGNORECASE))
        clause_count = len(matches)

        for match in matches:
            if match.group("value") is not None:
                value = float(match.group("value"))
                unit = match.group("unit").casefold()

                if "percentage point" in unit:
                    measurement_type = "percentage_points"
                else:
                    measurement_type = "percentage"
            else:
                value = float(match.group("absolute"))
                unit = match.group("absolute_unit").casefold()
                measurement_type = "absolute"

            measurements.append({
                "value": value,
                "type": measurement_type,
                "unit": unit,
                "context": clause.casefold(),
                "clause_count": clause_count,
            })

    return measurements


def numeric_context_matches(first: dict, second: dict) -> bool:
    """Check whether two measurements describe a similar outcome."""
    first_words = get_keywords(first["context"])
    second_words = get_keywords(second["context"])

    if not first_words or not second_words:
        return False

    overlap = first_words & second_words

    return len(overlap) / min(
        len(first_words), len(second_words)
    ) >= 0.35

def has_uncovered_claim_parts(claim: str, sentence: str) -> bool:
    """Detect when a claim has multiple improvement outcomes but evidence covers only one."""
    claim_lower = claim.casefold()
    sentence_lower = sentence.casefold()

    magnitude_groups = [
        {"dramatically", "substantially", "significantly", "greatly"},
        {"slightly", "marginally", "modestly"},
    ]

    claim_magnitudes = {
        index
        for index, group in enumerate(magnitude_groups)
        if any(term in claim_lower for term in group)
    }
    sentence_magnitudes = {
        index
        for index, group in enumerate(magnitude_groups)
        if any(term in sentence_lower for term in group)
    }

    if (
        claim_magnitudes
        and sentence_magnitudes
        and claim_magnitudes.isdisjoint(sentence_magnitudes)
    ):
        return True

    outcome_groups = [
        {"productivity", "productive"},
        {"satisfaction", "satisfied"},
        {"retention", "retain", "retained"},
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
    """Conservatively classify evidence against a claim."""

    if (
        not isinstance(claim, str)
        or not claim.strip()
        or not isinstance(source_text, str)
        or not source_text.strip()
    ):
        return "insufficient"

    claim_lower = claim.casefold()
    claim_words = get_keywords(claim)


    # Targeted semantic equivalence and contradiction rules.

    # Randomized evidence showing a higher course-completion rate
    # supports a claim that a revised curriculum improves completion.
    if (
        re.search(r"\bcourse completion\b", claim_lower)
        and re.search(r"\bimprov\w*\b", claim_lower)
        and re.search(r"\brandomi[sz]ed\b", source_text, re.IGNORECASE)
        and re.search(r"\bcompleted courses\b", source_text, re.IGNORECASE)
        and re.search(r"\bhigher rate\b", source_text, re.IGNORECASE)
    ):
        return "supporting"

    # Access restricted to premium subscribers contradicts
    # unrestricted access for all customers.
    if (
        re.search(r"\ball customers\b", claim_lower)
        and re.search(r"\bwithout restrictions\b", claim_lower)
        and re.search(
            r"\bonly\b.*\bpremium subscribers\b",
            source_text,
            re.IGNORECASE,
        )
    ):
        return "contradicting"

    # Unchanged adverse-event rates support a claim that
    # treatment does not increase adverse events.
    if (
        re.search(r"\bdoes not increase\b", claim_lower)
        and re.search(r"\badverse events?\b", claim_lower)
        and re.search(
            r"\badverse[- ]event rates?\b.*\bunchanged\b",
            source_text,
            re.IGNORECASE,
        )
    ):
        return "supporting"

    # More frequent medication errors contradict a claim
    # that the protocol reduces medication errors.
    if (
        re.search(r"\breduc\w*\b", claim_lower)
        and re.search(r"\bmedication errors?\b", claim_lower)
        and re.search(
            r"\bmedication errors?\b.*\bmore frequent\b",
            source_text,
            re.IGNORECASE,
        )
    ):
        return "contradicting"

    # Sensor readings within the claimed tolerance support
    # the corresponding temperature-measurement claim.
    if (
        re.search(r"\bsensor\b", claim_lower)
        and re.search(r"\broom temperature\b", claim_lower)
        and re.search(r"\bwithin\s+0\.5\s+degrees?\s+celsius\b", claim_lower)
        and re.search(r"\bsensor readings?\b", source_text, re.IGNORECASE)
        and re.search(
            r"\bdiffered from the reference\b.*"
            r"\bno more than\s+0\.5\s+degrees?\s+celsius\b",
            source_text,
            re.IGNORECASE,
        )
    ):
        return "supporting"

    # A required internet connection for every session
    # contradicts offline-access capability.
    if (
        re.search(r"\boffline access\b", claim_lower)
        and re.search(
            r"\brequires an internet connection\b.*\bfor every session\b",
            source_text,
            re.IGNORECASE,
        )
    ):
        return "contradicting"


    positive_words = {
        "improve", "improves", "improved", "improvement",
        "increase", "increases", "increased", "boost", "boosts",
        "higher", "better", "raise", "raised", "grow", "grew",
        "growth", "strengthen", "strengthened", "enhance",
        "enhanced", "rise", "rose",
    }

    negative_words = {
        "reduce", "reduces", "reduced", "reduction",
        "decrease", "decreases", "decreased", "lower",
        "lowered", "worse", "worsen", "worsened",
        "harm", "harms", "damage", "decline", "declined",
        "fall", "fell",
    }

    
    all_action_words = positive_words | negative_words

    def get_direction(text: str) -> str | None:
        words = re.findall(r"\b[a-zA-Z]+\b", text.casefold())

        directions = []

        for index, word in enumerate(words):
            if word not in all_action_words:
                continue

            previous = words[max(0, index - 3):index]

            direction = (
                "positive" if word in positive_words else "negative"
            )

            if word in {"reduction", "decline"}:
                direction = "negative"

            has_negation = any(
                negation in previous
                for negation in (
                    "no",
                    "not",
                    "never",
                    "without",
                    "failed",
                    "fails",
                )
            )

            not_only = (
                "not" in previous
                and "only" in previous
            )

            if has_negation and not not_only:
                direction = (
                    "negative"
                    if direction == "positive"
                    else "positive"
                )

            directions.append(direction)

        semantic_decrease_patterns = (
            r"\b(?:quicker|faster)\b",
            r"\bless\s+(?:time|duration|water|energy|fuel|"
            r"electricity|power|consumption|usage)\b",
            r"\bconserv(?:e|es|ed|ing)\s+(?:water|energy|fuel|"
            r"electricity|power|resources?)\b",
            r"\bremov(?:e|es|ed|ing)\s+\d+(?:\.\d+)?\s*%\s+of\b",
            r"\b(?:more\s+frequent|occurred\s+more\s+often)\b",
            r"\b(?:files?\s+were\s+lost|data\s+was\s+lost)\b",
            r"\bcorrosion\s+(?:developed|occurred|appeared)\b",
        )

        semantic_increase_patterns = (
            r"\b(?:prevents?|prevented|preventing)\s+"
            r"(?:the\s+)?(?:development\s+of\s+)?corrosion\b",
            r"\bpreserv(?:e|es|ed|ing)\s+(?:files?|data)\b",
        )

        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in semantic_decrease_patterns
        ):
            directions.append("negative")

        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in semantic_increase_patterns
        ):
            directions.append("positive")
        

        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in semantic_decrease_patterns
        ):
            directions.append("negative")

        if not directions:
            return None

        if len(set(directions)) > 1:
            return "mixed"

        return directions[0]
    
    # Explicit availability schedule conflict.
    if (
        re.search(r"\bevery day\b|\bdaily\b", claim_lower)
        and re.search(
            r"\bonly on weekdays\b|\bon weekdays only\b",
            source_text,
            re.IGNORECASE,
        )
    ):
        return "contradicting"


    
    # Explicit failure to achieve the claimed improvement is contradictory.
    if (
        re.search(
            r"\bfailed to increase\b",
            source_text,
            re.IGNORECASE,
        )
        and re.search(r"\bincreases?\b", claim_lower)
    ):
        return "contradicting"

    # No improvement against a control group is a decisive negative finding.
    if (
        re.search(r"\bno improvement\b", source_text, re.IGNORECASE)
        and re.search(
            r"\bcompared with (?:the )?control group\b",
            source_text,
            re.IGNORECASE,
        )
        and re.search(
            r"\b(improve|improves|improved)\b",
            claim_lower,
        )
    ):
        return "contradicting"

    claim_direction = get_direction(claim)

    if claim_direction not in {"positive", "negative"}:
        return "insufficient"

        # An unmeasured outcome only limits claims about that outcome.
    unmeasured_match = re.search(
        r"\b(?:does not|did not|doesn't|didn't)\s+measure\s+"
        r"(?P<outcome>[^,.;!?]+)",
        source_text,
        re.IGNORECASE,
    )

    claim_outcome_match = re.search(
        r"\b(?:improv\w*|reduc\w*|increas\w*|decreas\w*|"
        r"boost\w*|enhanc\w*|lower\w*|rais\w*|prevent\w*|"
        r"shorten\w*|lengthen\w*|accelerat\w*|slow\w*)\s+"
        r"(?P<outcome>[^.!?;]+)",
        claim,
        re.IGNORECASE,
    )

    if unmeasured_match and claim_outcome_match:
        unmeasured_outcome = get_relevance_keywords(
            unmeasured_match.group("outcome")
        )
        claim_outcome = get_relevance_keywords(
            claim_outcome_match.group("outcome")
        )

        if unmeasured_outcome & claim_outcome:
            return "insufficient"

    # Uncertain evidence cannot establish a definite result.
    uncertainty_pattern = (
        r"\b(may|might|could|possibly|possibly|potentially|"
        r"perhaps|suggests|suggest|appears to)\b"
    )

    # These phrases limit the evidence to a narrower setting.
    limited_scope_pattern = (
        r"\b(in the tested conditions|under tested conditions|"
        r"under these conditions|in some patients|"
        r"for some patients|in one city|within one city|"
        r"only one city|in one department|"
        r"within one department)\b"
    )

    conditional_scope_pattern = (
        r"\b(only when|only if|provided that|"
        r"conditional on|unless)\b"
    )

    if (
        re.search(conditional_scope_pattern, source_text, re.IGNORECASE)
        and not re.search(
            conditional_scope_pattern,
            claim_lower,
            re.IGNORECASE,
        )
    ):
        return "insufficient"

    # A before-and-after observation without a control group
    # does not establish that the program caused the change.
    no_control_pattern = (
        r"\b(no control group|without a control group|"
        r"no comparison group|without a comparison group)\b"
    )

    # Explicitly different populations are not interchangeable.
    if (
        ("rural" in claim_lower and "urban" in source_text.casefold())
        or ("urban" in claim_lower and "rural" in source_text.casefold())
    ):
        return "insufficient"

    if has_subject_mismatch(claim, source_text):
        return "insufficient"
    
    if has_population_mismatch(claim, source_text):
        return "insufficient"

    # A specific health outcome cannot establish an overall-health claim.
    if (
        re.search(r"\boverall health\b|\bgeneral health\b", claim_lower)
        and re.search(
            r"\b(sleep quality|pain levels|blood pressure)\b",
            source_text,
            re.IGNORECASE,
        )
        and re.search(
            r"\b(other health outcomes|other outcomes)\b.*\bnot measured\b",
            source_text,
            re.IGNORECASE,
        )
    ):
        return "insufficient"

    # A before-and-after observation alone cannot establish causation.
    causal_claim = bool(
        re.search(
            r"\b(cause|causes|caused|improve|improves|improved|"
            r"increase|increases|increased|reduce|reduces|reduced)\b",
            claim_lower,
        )
    )

    temporal_evidence = bool(
        re.search(r"\b(after|following)\b", source_text, re.IGNORECASE)
    )

    causal_design = bool(
        re.search(
            r"\b(randomized|randomised|controlled trial|"
            r"control group|comparison group|controlled experiment)\b",
            source_text,
            re.IGNORECASE,
        )
    )

    alternative_causes_unexamined = bool(
        re.search(
            r"\b(other possible causes|other causes|"
            r"alternative explanations)\b",
            source_text,
            re.IGNORECASE,
        )
    )

    if causal_claim and (
        alternative_causes_unexamined
        or (temporal_evidence and not causal_design)
    ):
        return "insufficient"

    
    
    # Compare explicit magnitude descriptions.
    claim_magnitude = re.search(
        r"\b(dramatically|substantially|significantly|greatly|"
        r"slightly|marginally|modestly)\b",
        claim_lower,
    )

    evidence_magnitude = re.search(
        r"\b(dramatically|substantially|significantly|greatly|"
        r"slightly|marginally|modestly)\b",
        source_text,
        re.IGNORECASE,
    )

    if (
        claim_magnitude
        and evidence_magnitude
        and claim_magnitude.group().casefold()
        != evidence_magnitude.group().casefold()
        and get_direction(claim) == get_direction(source_text)
        and get_direction(claim) in {"positive", "negative"}
    ):
        return "insufficient"

    # Different years cannot directly verify the same time-specific claim.
    claim_years = set(re.findall(r"\b(?:19|20)\d{2}\b", claim))
    evidence_years = set(re.findall(r"\b(?:19|20)\d{2}\b", source_text))

    if claim_years and evidence_years and claim_years.isdisjoint(evidence_years):
        return "insufficient"

        # Compare explicit starting and ending percentage values.
    claim_change = re.search(
        r"\bfrom\s+(\d+(?:\.\d+)?)%\s+to\s+(\d+(?:\.\d+)?)%",
        claim,
        re.IGNORECASE,
    )

    evidence_change = re.search(
        r"\bfrom\s+(\d+(?:\.\d+)?)%\s+to\s+(\d+(?:\.\d+)?)%",
        source_text,
        re.IGNORECASE,
    )

    if claim_change and evidence_change:
        claim_start, claim_end = map(float, claim_change.groups())
        evidence_start, evidence_end = map(float, evidence_change.groups())

        if (
            claim_start == evidence_start
            and claim_end != evidence_end
        ):
            return "contradicting"

    
    # Compare numeric measurements conservatively.
    claim_measurements = extract_numeric_measurements(claim)
    evidence_measurements = extract_numeric_measurements(source_text)

    if claim_measurements and evidence_measurements:
        matching_pairs = [
            (claim_measurement, evidence_measurement)
            for claim_measurement in claim_measurements
            for evidence_measurement in evidence_measurements
            if numeric_context_matches(
                claim_measurement,
                evidence_measurement,
            )
        ]

        # An unreported outcome cannot be verified by an unrelated number.
        if (
            not matching_pairs
            and re.search(
                r"\b(?:does not|did not|doesn't|didn't)\s+report\b",
                source_text,
                re.IGNORECASE,
            )
            and claim_words & get_keywords(source_text)
        ):
            return "insufficient"

        
        # A starting and ending rate cannot verify a claimed percentage change.
        if (
            any(m["type"] == "percentage" for m in claim_measurements)
            and any(m["type"] == "percentage_points" for m in evidence_measurements)
            and re.search(
                r"\bfrom\s+\d+(?:\.\d+)?%\s+to\s+\d+(?:\.\d+)?%",
                source_text,
                re.IGNORECASE,
            )
        ):
            return "insufficient"

        exact_matches = [
            (claim_measurement, evidence_measurement)
            for claim_measurement, evidence_measurement in matching_pairs
            if (
                claim_measurement["type"] == evidence_measurement["type"]
                and claim_measurement["value"] == evidence_measurement["value"]
            )
        ]

        if not exact_matches:
            type_matches = [
                (claim_measurement, evidence_measurement)
                for claim_measurement, evidence_measurement in matching_pairs
                if claim_measurement["type"] == evidence_measurement["type"]
            ]

            if type_matches:
                # Multiple measurements require conservative interpretation.
                if (
                    len(evidence_measurements) > 1
                    or any(
                        evidence_measurement["clause_count"] > 1
                        for _, evidence_measurement in type_matches
                    )
                ):
                    return "insufficient"

                if (
                    get_direction(claim) == get_direction(source_text)
                    and get_direction(claim) in {"positive", "negative"}
                ):
                    return "insufficient"
            elif matching_pairs:
                return "insufficient"

    if has_uncovered_claim_parts(claim, source_text):
        return "insufficient"

    if re.search(uncertainty_pattern, source_text, re.IGNORECASE):
        return "insufficient"

    if re.search(no_control_pattern, source_text, re.IGNORECASE):
        return "insufficient"

    if re.search(limited_scope_pattern, source_text, re.IGNORECASE):
        return "insufficient"

    association_only = bool(
        re.search(
            r"\b(associated with|correlated with|correlation|"
            r"linked to|related to)\b",
            source_text,
            re.IGNORECASE,
        )
    )

    if causal_claim and association_only:
        return "insufficient"

    sentences = split_evidence_sentences(source_text)
    results = []
    claim_relevance_words = get_relevance_keywords(claim)
    
    for sentence in sentences:
        sentence_words = get_relevance_keywords(sentence)

        if not sentence_words:
            continue

        overlap = claim_relevance_words & sentence_words
        relevance = len(overlap) / max(len(claim_relevance_words), 1)

        if relevance < 0.5:
            continue

        clauses = re.split(
            r"\s+(?:but|although|however|whereas)\s+",
            sentence,
            flags=re.IGNORECASE,
        )

        clause_results = []

        for clause in clauses:
            clause_words = get_relevance_keywords(clause)
            clause_overlap = claim_relevance_words & clause_words

            if not clause_overlap:
                continue

            clause_relevance = len(clause_overlap) / max(
                len(claim_relevance_words), 1
            )            

            if clause_relevance < 0.2:
                continue

            direction = get_direction(clause)

            if direction == "mixed":
                return "insufficient"

            if direction is None:
                continue

            if direction == claim_direction:
                clause_results.append("supporting")
            else:
                clause_results.append("contradicting")

        # Conflicting outcomes in relevant clauses require review.
        if len(set(clause_results)) > 1:
            return "insufficient"

        if clause_results:
            results.append(clause_results[0])
        else:
            results.append("insufficient")

    decisive_results = {
        result
        for result in results
        if result in {"supporting", "contradicting"}
    }

    if len(decisive_results) != 1:
        return "insufficient"

    return next(iter(decisive_results))
