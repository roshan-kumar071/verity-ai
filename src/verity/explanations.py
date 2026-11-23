
import re

from verity.evidence import (
    classify_evidence,
    extract_numeric_measurements,
    has_population_mismatch,
    has_subject_mismatch,
    has_uncovered_claim_parts,
    numeric_context_matches,
    split_evidence_sentences,
)

VALID_CLASSIFICATIONS = {
    "supporting",
    "contradicting",
    "insufficient",
}


def _result(reason_code, reason, evidence_signal, explanation):
    return {
        "reason_code": reason_code,
        "reason": reason,
        "evidence_signal": evidence_signal,
        "explanation": explanation,
    }


def _get_outcome_direction(text):
    text = text.casefold()

    increase_pattern = (
        r"\b(increase|increases|increased|increasing|"
        r"improve|improves|improved|improving|"
        r"rise|rises|rose|rising|higher|greater|"
        r"up|went up|goes up|grew|growth)\b"
    )

    decrease_pattern = (
        r"\b(decrease|decreases|decreased|decreasing|"
        r"reduce|reduces|reduced|reducing|"
        r"decline|declines|declined|declining|"
        r"fall|falls|fell|falling|lower|less|"
        r"went down|goes down|dropped|drop|"
        r"declined)\b"
    )

    negation_pattern = (
        r"\b(?:not|never|no longer|"
        r"did not|does not|do not|"
        r"has not|have not|had not|"
        r"failed to|unable to|without)\b"
    )

    def has_negation(match):
        preceding_text = text[:match.start()]
        recent_words = preceding_text.split()[-4:]

        return bool(
            re.search(
                negation_pattern,
                " ".join(recent_words),
            )
        )

    double_negation = re.search(
        r"\b(?:did not|does not|do not|"
        r"has not|have not|had not)\s+"
        r"(?:fail|fails|failed)\s+to\s+"
        r"(?:improve|increase|raise|boost)\b",
        text,
    )

    if double_negation:
        return "increase"

    increase_matches = [
        match
        for match in re.finditer(increase_pattern, text)
        if not has_negation(match)
    ]

    decrease_matches = [
        match
        for match in re.finditer(decrease_pattern, text)
        if not has_negation(match)
    ]

    if increase_matches and not decrease_matches:
        return "increase"

    if decrease_matches and not increase_matches:
        return "decrease"

    return None


def _has_mixed_clause_findings(claim, evidence):
    outcome_terms = (
        "productivity", "productive",
        "satisfaction", "satisfied",
        "retention", "retain", "retained",
        "performance", "health", "sleep",
        "learning", "outcomes", "speed",
    )

    claim_lower = claim.casefold()

    relevant_outcomes = [
        term for term in outcome_terms
        if term in claim_lower
    ]

    if not relevant_outcomes:
        return False

    sentences = split_evidence_sentences(evidence)

    for sentence in sentences:
        clauses = re.split(
            r"\s+(?:but|although|however|whereas)\s+",
            sentence,
            flags=re.IGNORECASE,
        )

        if len(clauses) < 2:
            continue

        supporting_outcomes = set()
        contradicting_outcomes = set()

        for clause in clauses:
            clause_lower = clause.casefold()

            matched_outcomes = [
                term for term in relevant_outcomes
                if term in clause_lower
            ]

            if not matched_outcomes:
                continue


            claim_direction = _get_outcome_direction(claim)
            clause_direction = _get_outcome_direction(clause)

            if not claim_direction:
                continue

            negated_direction = re.search(
                r"\b(?:not|never|no longer|did not|does not|"
                r"do not|has not|have not|had not|"
                r"failed to|unable to|without)\s+"
                r"(?:increase|improve|rise|reduce|decrease|"
                r"decline|fall|raise|boost)\b",
                clause_lower,
            )

            if negated_direction:
                contradicting_outcomes.update(matched_outcomes)

            elif clause_direction == claim_direction:
                supporting_outcomes.update(matched_outcomes)

            elif clause_direction:
                contradicting_outcomes.update(matched_outcomes)

        if supporting_outcomes and contradicting_outcomes:
            return True

    return False


def _has_partially_covered_compound_claim(claim, evidence):
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were",
        "has", "have", "had", "and", "or", "but",
        "in", "on", "under", "with", "for", "to",
        "of", "its", "it", "that", "this", "their",
        "every", "all", "well",
    }

    claim_parts = re.split(
        r"\s*,\s*|\s+\band\b\s+",
        claim,
        flags=re.IGNORECASE,
    )

    if len(claim_parts) < 2:
        return False

    covered_parts = 0
    uncovered_parts = 0

    evidence_words = {
        word
        for word in re.findall(r"\b[a-z]+\b", evidence.casefold())
        if word not in stop_words
    }

    for part in claim_parts:
        part_words = {
            word
            for word in re.findall(r"\b[a-z]+\b", part.casefold())
            if word not in stop_words
        }

        if not part_words:
            continue

        overlap = part_words & evidence_words

        if len(overlap) / len(part_words) > 0.5:
            covered_parts += 1
        else:
            uncovered_parts += 1

    return covered_parts > 0 and uncovered_parts > 0


def explain_classification(
    claim: str,
    evidence: str,
    classification: str,
) -> dict:
    """Generate a structured explanation for an evidence decision."""

    if classification not in VALID_CLASSIFICATIONS:
        raise ValueError("Invalid classification label.")

    if (
        not isinstance(claim, str)
        or not claim.strip()
        or not isinstance(evidence, str)
        or not evidence.strip()
    ):
        return _result(
            "missing_input",
            "Claim or evidence is missing.",
            "Missing information",
            "A reliable comparison cannot be made because "
            "the claim or evidence is empty.",
        )

    sentences = split_evidence_sentences(evidence)

    if not sentences:
        sentences = [evidence]


    subject_mismatch = all(
        has_subject_mismatch(claim, sentence)
        for sentence in sentences
    )

    population_mismatch = all(
        has_population_mismatch(claim, sentence)
        for sentence in sentences
    )

    if subject_mismatch:
        return _result(
            "subject_mismatch",
            "Evidence discusses a different subject.",
            "Subject mismatch",
            "The evidence discusses a topic different from "
            "the subject described in the claim.",
        )

    if population_mismatch:
        return _result(
            "population_mismatch",
            "Evidence concerns a different population.",
            "Population mismatch",
            "The evidence concerns a different population "
            "or group from the one specified in the claim.",
        )

    claim_lower = claim.casefold()
    combined_evidence = " ".join(sentences)

    limited_scope = re.search(
        r"\b(not tested|untested|only in|limited to|"
        r"in the tested conditions|under tested conditions|"
        r"under these conditions|in some patients|"
        r"for some patients|in one city|within one city|"
        r"only when|only if|provided that|conditional on|unless)\b",
        evidence,
        re.IGNORECASE,
    )

    if classification == "insufficient" and limited_scope:
        return _result(
            "limited_scope",
            "Evidence has limited scope.",
            "Scope limitation",
            "The evidence covers only limited conditions "
            "and does not establish the full claim.",
        )

    if (
        classification == "insufficient"
        and _has_mixed_clause_findings(claim, evidence)):
        return _result(
            "mixed_findings",
            "Evidence contains conflicting findings.",
            "Mixed outcome directions",
            "Different parts of the evidence support and "
            "contradict the claim, so a single clear conclusion "
            "cannot be established.",
        )

    if (
        classification == "insufficient"
        and _has_partially_covered_compound_claim(
            claim,
            combined_evidence,
        )
    ):
        return _result(
            "uncovered_claim_parts",
            "Evidence does not cover every part of the claim.",
            "Incomplete claim coverage",
            "The evidence addresses some parts of the claim "
            "but does not provide enough information about "
            "the remaining parts.",
        )

    outcome_terms = [
        "productivity", "productive",
        "satisfaction", "satisfied",
        "retention", "retain", "retained",
        "performance", "health", "sleep",
        "learning", "outcomes", "speed",
    ]

    claim_outcome_count = sum(
        1 for term in outcome_terms if term in claim_lower
    )

    has_claim_magnitude = re.search(
        r"\b(dramatically|substantially|significantly|"
        r"greatly|slightly|marginally|modestly)\b",
        claim_lower,
    )

    if (
        (claim_outcome_count >= 2 or has_claim_magnitude)
        and has_uncovered_claim_parts(claim, combined_evidence)
    ):
        return _result(
            "uncovered_claim_parts",
            "Evidence does not cover every part of the claim.",
            "Incomplete outcome coverage",
            "The evidence does not address all the outcomes "
            "or magnitude described in the claim.",
        )

    uncertainty = re.search(
        r"\b(may|might|could|possibly|potentially|perhaps|"
        r"suggests|suggest|appears to)\b",
        evidence,
        re.IGNORECASE,
    )

    if classification == "insufficient" and uncertainty:
        return _result(
            "uncertain_evidence",
            "Evidence contains uncertain findings.",
            "Uncertainty language",
            "The evidence uses uncertain language and "
            "does not establish a definite conclusion.",
        )


    claim_measurements = extract_numeric_measurements(claim)
    evidence_measurements = extract_numeric_measurements(evidence)

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

    def units_are_compatible(first, second):
        unit_groups = [
            {"%", "percent"},
            {"unit", "units"},
            {"point", "points"},
            {"hour", "hours"},
            {"day", "days"},
            {"minute", "minutes"},
            {"second", "seconds"},
            {"kg", "kilogram", "kilograms"},
            {"mg"},
            {"gram", "grams"},
            {"percentage point", "percentage points"},
        ]

        first_unit = first["unit"].casefold()
        second_unit = second["unit"].casefold()

        return any(
            first_unit in group and second_unit in group
            for group in unit_groups
        ) or first_unit == second_unit

    def get_measurement_outcomes(measurement):
        context = measurement["context"].casefold()

        return {
            index
            for index, group in enumerate(outcome_groups)
            if any(
                re.search(r"\b" + re.escape(term) + r"\b", context)
                for term in group
            )
        }



    possible_pairs = []

    for claim_index, first in enumerate(claim_measurements):
        for evidence_index, second in enumerate(evidence_measurements):
            if not (
                first["type"] == second["type"]
                and units_are_compatible(first, second)
                and numeric_context_matches(first, second)
                and not has_population_mismatch(
                    claim,
                    second["context"],
                )
                and (
                    not get_measurement_outcomes(first)
                    or get_measurement_outcomes(first)
                    == get_measurement_outcomes(second)
                )
            ):
                continue

            possible_pairs.append((
                claim_index,
                evidence_index,
                first,
                second,
                first["value"] == second["value"],
            ))

    possible_pairs.sort(
        key=lambda pair: (
            not pair[4],
            pair[0],
            pair[1],
        )
    )

    compatible_evidence = {
        index: []
        for index in range(len(claim_measurements))
    }

    for pair in possible_pairs:
        compatible_evidence[pair[0]].append(pair[1])

    matching_by_evidence = {}

    def assign_claim(claim_index, visited_evidence):
        for evidence_index in compatible_evidence[claim_index]:
            if evidence_index in visited_evidence:
                continue

            visited_evidence.add(evidence_index)

            previous_claim = matching_by_evidence.get(
                evidence_index
            )

            if (
                previous_claim is None
                or assign_claim(previous_claim, visited_evidence)
            ):
                matching_by_evidence[evidence_index] = claim_index
                return True

        return False

    for claim_index in range(len(claim_measurements)):
        assign_claim(claim_index, set())

    matching_indices = sorted(
        (
            claim_index,
            evidence_index,
        )
        for evidence_index, claim_index
        in matching_by_evidence.items()
    )

    matching_pairs = [
        (
            claim_measurements[claim_index],
            evidence_measurements[evidence_index],
        )
        for claim_index, evidence_index in matching_indices
    ]


    if matching_pairs:
        numerical_details = []

        for first, second in matching_pairs:
            claim_value = first["value"]
            evidence_value = second["value"]

            claim_unit = first["unit"]
            evidence_unit = second["unit"]

            claim_display = (
                f"{claim_value:g}{claim_unit}"
                if claim_unit in {"%", "percent"}
                else f"{claim_value:g} {claim_unit}"
            )

            evidence_display = (
                f"{evidence_value:g}{evidence_unit}"
                if evidence_unit in {"%", "percent"}
                else f"{evidence_value:g} {evidence_unit}"
            )

            if claim_value == evidence_value:
                detail = (
                    f"Both claim and evidence report {claim_display}."
                )
            else:
                detail = (
                    f"The claim reports {claim_display}, "
                    f"while the evidence reports {evidence_display}. "
                    f"The numerical values differ."
                )

            if detail not in numerical_details:
                numerical_details.append(detail)

        numerical_detail = " ".join(numerical_details)



        claim_direction = _get_outcome_direction(claim)
        evidence_direction = _get_outcome_direction(evidence)

        direction_conflict = (
            claim_direction is not None
            and evidence_direction is not None
            and claim_direction != evidence_direction
        )

        if direction_conflict:
            numerical_reason = (
                "Comparable numerical evidence reports an "
                "opposite outcome direction."
            )
            numerical_explanation = (
                numerical_detail
                + f" The claim indicates {claim_direction}, "
                f"but the evidence indicates {evidence_direction}. "
                "The outcome directions conflict."
            )

        elif classification == "supporting":
            numerical_reason = (
                "Comparable numerical evidence is present."
            )

            numerical_explanation = (
                numerical_detail
                + " The supplied classification is supporting. "
                "This numerical comparison provides context but "
                "does not independently establish the classification."
            )

        elif classification == "contradicting":
            numerical_reason = (
                "Comparable numerical evidence conflicts with the claim."
            )
            numerical_explanation = (
                numerical_detail
                + " The reported outcome conflicts with the claim."
            )

        else:
            numerical_reason = (
                "Numerical evidence is available but inconclusive."
            )
            numerical_explanation = (
                numerical_detail
                + " The numerical comparison alone does not "
                "establish a clear conclusion."
            )

        return _result(
            "numerical_evidence",
            numerical_reason,
            "Numerical comparison",
            numerical_explanation,
        )

    claim_lower = claim.casefold()

    causal_claim = bool(
        re.search(
            r"\b(cause|causes|caused|improve|improves|improved|"
            r"increase|increases|increased|reduce|reduces|reduced)\b",
            claim_lower,
        )
    )

    association_only = bool(
        re.search(
            r"\b(associated with|correlated with|correlation|"
            r"linked to|related to)\b",
            evidence,
            re.IGNORECASE,
        )
    )

    temporal_evidence = bool(
        re.search(
            r"\b(before|after|following)\b",
            evidence,
            re.IGNORECASE,
        )
    )

    no_control = bool(
        re.search(
            r"\b(no control group|without a control group|"
            r"no comparison group|without a comparison group|"
            r"there (?:was|were) no control group|"
            r"there (?:was|were) no comparison group)\b",
            evidence,
            re.IGNORECASE,
        )
    )

    causal_design = bool(
        re.search(
            r"\b(randomized|randomised|controlled trial|"
            r"controlled experiment|"
            r"(?:with|using|compared with) "
            r"(?:the |a )?(?:control|comparison) group)\b",
            evidence,
            re.IGNORECASE,
        )
    )

    if classification == "insufficient" and causal_claim:
        if association_only:
            return _result(
                "association_only",
                "Evidence establishes association, not causation.",
                "Correlation or association",
                "The evidence reports an association but does not "
                "establish that one factor caused the outcome.",
            )

        if temporal_evidence and no_control and not causal_design:
            return _result(
                "causal_limitation",
                "Evidence cannot establish causation.",
                "Before-and-after observation without a control group",
                "The evidence describes a change over time without "
                "a control or comparison group to establish causation.",
            )


    supporting_sentences = [
        sentence
        for sentence in sentences
        if classify_evidence(claim, sentence) == "supporting"
    ]

    contradicting_sentences = [
        sentence
        for sentence in sentences
        if classify_evidence(claim, sentence) == "contradicting"
    ]

    if supporting_sentences and contradicting_sentences:
        supporting_details = " ".join(supporting_sentences)
        contradicting_details = " ".join(contradicting_sentences)

        mixed_explanation = (
            f"Supporting finding: {supporting_details} "
            f"Contradicting finding: {contradicting_details}"
        )

        return _result(
            "mixed_findings",
            "Evidence contains conflicting findings.",
            "Mixed outcome directions",
            mixed_explanation,
        )

    if classification == "supporting":
        outcome_terms = [
            "productivity", "productive",
            "satisfaction", "satisfied",
            "retention", "retain", "retained",
            "performance", "health", "sleep",
            "learning", "outcomes", "speed",
        ]

        shared_outcomes = [
            term
            for term in outcome_terms
            if term in claim.casefold()
            and term in evidence.casefold()
        ]

        claim_direction = _get_outcome_direction(claim)
        evidence_direction = _get_outcome_direction(evidence)

        if shared_outcomes and claim_direction and evidence_direction:
            outcome_text = ", ".join(shared_outcomes)
            supporting_explanation = (
                f"The evidence reports {evidence_direction} in "
                f"{outcome_text}, consistent with the claim's "
                f"{claim_direction} direction."
            )
        elif shared_outcomes:
            outcome_text = ", ".join(shared_outcomes)
            supporting_explanation = (
                f"The evidence reports findings about {outcome_text} "
                "that are consistent with the claim."
            )
        else:
            supporting_explanation = (
                "The evidence reports an outcome consistent "
                "with the claim."
            )

        return _result(
            "outcome_alignment",
            "Evidence supports the claimed outcome.",
            "Outcome direction alignment",
            supporting_explanation,
        )

    if classification == "contradicting":
        outcome_terms = [
            "productivity", "productive",
            "satisfaction", "satisfied",
            "retention", "retain", "retained",
            "performance", "health", "sleep",
            "learning", "outcomes", "speed",
        ]

        shared_outcomes = [
            term
            for term in outcome_terms
            if term in claim.casefold()
            and term in evidence.casefold()
        ]

        claim_direction = _get_outcome_direction(claim)
        evidence_direction = _get_outcome_direction(evidence)

        if shared_outcomes and claim_direction and evidence_direction:
            outcome_text = ", ".join(shared_outcomes)
            contradicting_explanation = (
                f"The evidence reports {evidence_direction} in "
                f"{outcome_text}, which conflicts with the claim's "
                f"{claim_direction} direction."
            )

        elif shared_outcomes and claim_direction:
            outcome_text = ", ".join(shared_outcomes)
            contradicting_explanation = (
                f"The evidence does not establish the claimed "
                f"{claim_direction} in {outcome_text}."
            )
        elif shared_outcomes:
            outcome_text = ", ".join(shared_outcomes)
            contradicting_explanation = (
                f"The evidence reports findings about {outcome_text} "
                "that conflict with the claim."
            )
        else:
            contradicting_explanation = (
                "The evidence reports an outcome that conflicts "
                "with the claim."
            )

        return _result(
            "outcome_contradiction",
            "Evidence opposes the claimed outcome.",
            "Outcome direction mismatch",
            contradicting_explanation,
        )

    return _result(
        "insufficient_evidence",
        "Evidence does not resolve the claim.",
        "Inconclusive evidence",
        "The available evidence does not provide enough "
        "information to confirm or contradict the claim.",
    )
