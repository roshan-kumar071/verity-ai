from verity.explanations import explain_classification


def test_supporting_explanation():
    result = explain_classification(
        "Remote work improves productivity.",
        "Remote work improves employee productivity.",
        "supporting",
    )

    assert result["reason_code"] == "outcome_alignment"
    assert result["evidence_signal"] == "Outcome direction alignment"
    assert result["explanation"]


def test_contradicting_explanation():
    result = explain_classification(
        "Medication errors decrease.",
        "Medication errors increased.",
        "contradicting",
    )

    assert result["reason_code"] == "outcome_contradiction"
    assert result["evidence_signal"] == "Outcome direction mismatch"


def test_limited_scope_explanation():
    result = explain_classification(
        "The device works in all weather conditions.",
        "The device was not tested in rain.",
        "insufficient",
    )

    assert result["reason_code"] == "limited_scope"

def test_untested_condition_is_explained_as_limited_scope():
    result = explain_classification(
        "The laptop operates reliably in every temperature condition.",
        "The laptop operates reliably in normal temperatures, but cold-weather performance was not tested.",
        "insufficient",
    )

    assert result["reason_code"] == "limited_scope"
    assert result["evidence_signal"] == "Scope limitation"
    assert "limited conditions" in result["explanation"]


def test_uncertain_evidence_explanation():
    result = explain_classification(
        "Remote work improves productivity.",
        "Remote work may improve productivity.",
        "insufficient",
    )

    assert result["reason_code"] == "uncertain_evidence"


def test_generic_insufficient_explanation():
    result = explain_classification(
        "Remote work improves productivity.",
        "The study discusses remote work.",
        "insufficient",
    )

    assert result["reason_code"] == "insufficient_evidence"


def test_invalid_classification():
    try:
        explain_classification("Claim", "Evidence", "unknown")
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"


def test_missing_input():
    result = explain_classification(
        "",
        "Some evidence.",
        "insufficient",
    )

    assert result["reason_code"] == "missing_input"


def test_association_only_explanation():
    result = explain_classification(
        "Remote work improves productivity.",
        "Remote work is associated with higher productivity.",
        "insufficient",
    )

    assert result["reason_code"] == "association_only"


def test_causal_limitation_explanation():
    result = explain_classification(
        "The program improves productivity.",
        "Productivity increased after the program, "
        "but there was no control group.",
        "insufficient",
    )

    assert result["reason_code"] == "causal_limitation"

def test_numerical_evidence_explanation():
    result = explain_classification(
        "The treatment reduces blood pressure by 10%.",
        "The treatment reduced blood pressure by 10%.",
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert result["evidence_signal"] == "Numerical comparison"
    assert result["reason"]
    assert result["explanation"]

def test_mixed_findings_explanation():
    result = explain_classification(
        "Remote work improves productivity.",
        "Remote work improves productivity in some teams. "
        "However, remote work reduces productivity in other teams.",
        "insufficient",
    )

    assert result["reason_code"] == "mixed_findings"
    assert result["evidence_signal"] == "Mixed outcome directions"
    assert result["reason"]
    assert result["explanation"]

def test_subject_mismatch_explanation():
    result = explain_classification(
        "Remote work improves productivity.",
        "Office lighting improves employee productivity.",
        "insufficient",
    )
    assert result["reason_code"] == "subject_mismatch"
    assert result["evidence_signal"] == "Subject mismatch"


def test_population_mismatch_explanation():
    result = explain_classification(
        "The treatment improves health in children.",
        "The treatment improves health in adults.",
        "insufficient",
    )
    assert result["reason_code"] == "population_mismatch"
    assert result["evidence_signal"] == "Population mismatch"


def test_mixed_findings_with_supporting_classification():
    result = explain_classification(
        "Remote work improves productivity.",
        "Remote work improves productivity in some teams. "
        "However, remote work reduces productivity in other teams.",
        "supporting",
    )

    assert result["reason_code"] == "mixed_findings"
    assert result["reason"]
    assert result["evidence_signal"] == "Mixed outcome directions"
    assert result["explanation"]
    assert "improves productivity" in result["explanation"].lower()
    assert "reduces productivity" in result["explanation"].lower()

def test_numerical_evidence_with_contradicting_classification():
    result = explain_classification(
        "The treatment reduces blood pressure by 10%.",
        "The treatment increases blood pressure by 10%.",
        "contradicting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert result["evidence_signal"] == "Numerical comparison"
    assert "conflict" in result["explanation"].lower()

def test_opposite_numeric_outcome_is_not_explained_as_alignment():
    result = explain_classification(
        "The treatment reduces blood pressure by 10%.",
        "The treatment increases blood pressure by 10%.",
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert "numerical" in result["evidence_signal"].lower()
    assert "conflict" in result["explanation"].lower()

def test_numerical_evidence_with_insufficient_classification():
    result = explain_classification(
        "The treatment reduces blood pressure by 10%.",
        "The treatment reduces blood pressure by 5%.",
        "insufficient",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert "inconclusive" in result["reason"].lower()

def test_supporting_explanation_is_evidence_specific():
    result = explain_classification(
        "Remote work improves productivity.",
        "Remote work improves employee productivity.",
        "supporting",
    )

    assert result["reason_code"] == "outcome_alignment"
    assert "productivity" in result["explanation"].lower()
    assert "evidence" in result["explanation"].lower()

def test_contradicting_explanation_is_evidence_specific():
    result = explain_classification(
        "Remote work improves productivity.",
        "Remote work reduces productivity.",
        "contradicting",
    )

    assert result["reason_code"] == "outcome_contradiction"
    assert "productivity" in result["explanation"].lower()
    assert "evidence" in result["explanation"].lower()

def test_outcome_direction_detection():
    from verity.explanations import _get_outcome_direction

    assert _get_outcome_direction("Productivity increased.") == "increase"
    assert _get_outcome_direction("Productivity decreased.") == "decrease"
    assert _get_outcome_direction("Productivity improved.") == "increase"
    assert _get_outcome_direction("Productivity declined.") == "decrease"
    assert _get_outcome_direction("Productivity changed.") is None
    assert _get_outcome_direction(
        "Productivity increased and decreased."
    ) is None

def test_supporting_explanation_mentions_outcome_direction():
    result = explain_classification(
        "Remote work increases productivity.",
        "Remote work increased productivity among participants.",
        "supporting",
    )

    assert result["reason_code"] == "outcome_alignment"
    assert "increase" in result["explanation"].lower()
    assert "productivity" in result["explanation"].lower()


def test_contradicting_explanation_mentions_opposite_direction():
    result = explain_classification(
        "Remote work increases productivity.",
        "Remote work decreased productivity among participants.",
        "contradicting",
    )

    assert result["reason_code"] == "outcome_contradiction"
    assert "decrease" in result["explanation"].lower()
    assert "increase" in result["explanation"].lower()
    assert "productivity" in result["explanation"].lower()

def test_outcome_direction_handles_negation():
    from verity.explanations import _get_outcome_direction

    assert _get_outcome_direction(
        "Productivity increased."
    ) == "increase"

    assert _get_outcome_direction(
        "Productivity decreased."
    ) == "decrease"

    assert _get_outcome_direction(
        "Productivity did not increase."
    ) is None

    assert _get_outcome_direction(
        "Productivity did not decrease."
    ) is None

    assert _get_outcome_direction(
        "Productivity has not improved."
    ) is None

    assert _get_outcome_direction(
        "Productivity never declined."
    ) is None

def test_contradicting_explanation_handles_negated_outcome():
    result = explain_classification(
        "Remote work increases productivity.",
        "Remote work did not increase productivity among participants.",
        "contradicting",
    )

    assert result["reason_code"] == "outcome_contradiction"
    assert "does not establish" in result["explanation"].lower()
    assert "increase" in result["explanation"].lower()
    assert "productivity" in result["explanation"].lower()


def test_mixed_findings_within_same_sentence():
    result = explain_classification(
        "Remote work improves productivity and job satisfaction.",
        (
            "Remote work improves productivity but reduces "
            "job satisfaction."
        ),
        "insufficient",
    )

    assert result["reason_code"] == "mixed_findings"
    assert "conflicting findings" in result["reason"].lower()
    assert "support" in result["explanation"].lower()
    assert "contradict" in result["explanation"].lower()


def test_outcome_direction_detects_common_alternatives():
    from verity.explanations import _get_outcome_direction

    assert _get_outcome_direction(
        "The error rate went up."
    ) == "increase"

    assert _get_outcome_direction(
        "The error rate became lower."
    ) == "decrease"

    assert _get_outcome_direction(
        "The recovery rate rose."
    ) == "increase"

    assert _get_outcome_direction(
        "The recovery rate fell."
    ) == "decrease"


def test_outcome_direction_handles_negated_actions():
    from verity.explanations import _get_outcome_direction

    assert _get_outcome_direction(
        "The treatment failed to improve recovery."
    ) is None

    assert _get_outcome_direction(
        "The treatment did not reduce symptoms."
    ) is None



def test_outcome_direction_handles_negated_comparisons():
    from verity.explanations import _get_outcome_direction

    assert _get_outcome_direction(
        "The error rate was not lower."
    ) is None

    assert _get_outcome_direction(
        "The recovery rate was not higher."
    ) is None


def test_outcome_direction_handles_nested_negation():
    from verity.explanations import _get_outcome_direction

    assert _get_outcome_direction(
        "The treatment did not fail to improve recovery."
    ) == "increase"

    assert _get_outcome_direction(
        "The treatment was unable to reduce symptoms."
    ) is None

def test_subject_mismatch_does_not_override_relevant_evidence():
    result = explain_classification(
        "Remote work improves employee productivity.",
        (
            "Remote work improves employee productivity. "
            "Office lighting improves classroom productivity."
        ),
        "supporting",
    )

    assert result["reason_code"] == "outcome_alignment"


def test_population_mismatch_does_not_override_relevant_evidence():
    result = explain_classification(
        "The treatment improves health in children.",
        (
            "The treatment improves health in children. "
            "The treatment improves health in adults."
        ),
        "supporting",
    )

    assert result["reason_code"] == "outcome_alignment"

def test_numerical_explanation_identifies_different_values():
    result = explain_classification(
        "The treatment reduces blood pressure by 10%.",
        "The treatment reduces blood pressure by 5%.",
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert "10%" in result["explanation"]
    assert "5%" in result["explanation"]
    assert "differ" in result["explanation"].lower()


def test_numerical_explanation_includes_multiple_measurements():
    result = explain_classification(
        "Productivity increases by 10% and employee satisfaction "
        "increases by 20%.",
        "Productivity increases by 10% and employee satisfaction "
        "increases by 15%.",
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert "10%" in result["explanation"]
    assert "20%" in result["explanation"]
    assert "15%" in result["explanation"]

def test_numerical_explanation_does_not_repeat_identical_measurements():
    result = explain_classification(
        "Productivity increases by 10%.",
        "Productivity increases by 10%.",
        "supporting",
    )

    explanation = result["explanation"]

    assert explanation.count("10%") == 1

def test_unrelated_numerical_measurements_are_not_matched():
    result = explain_classification(
        "Productivity increases by 10%.",
        "Employee satisfaction increases by 20%.",
        "supporting",
    )

    assert result["reason_code"] != "numerical_evidence"

def test_compound_numerical_claims_match_each_metric_separately():
    result = explain_classification(
        (
            "Productivity increases by 10%. "
            "Employee satisfaction increases by 20%."
        ),
        (
            "Productivity increases by 10%. "
            "Employee satisfaction increases by 15%."
        ),
        "supporting",
    )

    explanation = result["explanation"]

    assert result["reason_code"] == "numerical_evidence"
    assert "10%" in explanation
    assert "20%" in explanation
    assert "15%" in explanation
    assert explanation.count("10%") == 1


def test_percentage_and_percentage_points_are_not_equivalent():
    result = explain_classification(
        "Productivity increases by 10%.",
        "Productivity increases by 10 percentage points.",
        "supporting",
    )

    assert result["reason_code"] != "numerical_evidence"


def test_mixed_findings_with_negated_outcome():
    result = explain_classification(
        "Remote work improves productivity.",
        (
            "Remote work improves productivity in focused tasks, "
            "but does not improve productivity in collaborative tasks."
        ),
        "insufficient",
    )

    assert result["reason_code"] == "mixed_findings"

def test_incompatible_absolute_units_are_not_matched():
    result = explain_classification(
        "The machine processes 5 kg of material.",
        "The machine processes 5 hours of material.",
        "supporting",
    )

    assert result["reason_code"] != "numerical_evidence"


def test_equivalent_absolute_units_are_matched():
    result = explain_classification(
        "The machine processes 5 kg of material.",
        "The machine processes 5 kilograms of material.",
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"

def test_one_evidence_measurement_cannot_match_multiple_claims():
    result = explain_classification(
        (
            "Productivity increases by 10%. "
            "Productivity increases by 20%."
        ),
        "Productivity increases by 10%.",
        "supporting",
    )

    explanation = result["explanation"]

    assert result["reason_code"] == "numerical_evidence"
    assert "10%" in explanation
    assert "20%" not in explanation


def test_one_claim_measurement_cannot_match_multiple_evidence_values():
    result = explain_classification(
        "Productivity increases by 10%.",
        (
            "Productivity increases by 10%. "
            "Productivity increases by 12%."
        ),
        "supporting",
    )

    explanation = result["explanation"]

    assert result["reason_code"] == "numerical_evidence"
    assert "10%" in explanation
    assert "12%" not in explanation



def test_matching_finds_maximum_number_of_valid_pairs():
    result = explain_classification(
        (
            "Device: 20%. "
            "Display brightness screen: 30%."
        ),
        (
            "Device display brightness screen: 20%. "
            "Device processor temperature: 40%."
        ),
        "supporting",
    )

    explanation = result["explanation"]

    assert result["reason_code"] == "numerical_evidence"
    assert (
        "The claim reports 20%, while the evidence reports 40%."
        in explanation
    )
    assert (
        "The claim reports 30%, while the evidence reports 20%."
        in explanation
    )

def test_percentage_and_percentage_points_are_not_matched():
    result = explain_classification(
        "The success rate increased by 10%.",
        "The success rate increased by 10 percentage points.",
        "supporting",
    )

    assert result["reason_code"] != "numerical_evidence"

def test_partially_covered_compound_claim_is_explained():
    result = explain_classification(
        "The laptop is lightweight, has a long battery life, and performs well under heavy workloads.",
        "The laptop is lightweight and has a long battery life.",
        "insufficient",
    )

    assert result["reason_code"] == "uncovered_claim_parts"
    assert result["evidence_signal"] == "Incomplete claim coverage"
    assert "remaining parts" in result["explanation"]


def test_alternative_claim_does_not_trigger_partial_coverage():
    result = explain_classification(
        "The laptop supports Windows or Linux.",
        "The laptop supports Windows.",
        "insufficient",
    )

    assert result["reason_code"] != "uncovered_claim_parts"


def test_common_subject_words_do_not_prove_claim_coverage():
    result = explain_classification(
        "The laptop is lightweight and has a long battery life.",
        "The laptop weighs only 1.2 kg and lasts 12 hours.",
        "insufficient",
    )

    assert result["reason_code"] != "uncovered_claim_parts"


def test_fully_covered_compound_claim_does_not_trigger_partial_coverage():
    result = explain_classification(
        "The laptop is lightweight and has a long battery life.",
        "The laptop is lightweight and has a long battery life.",
        "insufficient",
    )

    assert result["reason_code"] != "uncovered_claim_parts"


def test_numeric_context_does_not_match_unrelated_measurements():
    from src.verity.evidence import (
        extract_numeric_measurements,
        numeric_context_matches,
    )

    claim = extract_numeric_measurements(
        "The treatment increased blood pressure by 10 units."
    )
    evidence = extract_numeric_measurements(
        "The treatment increased patient satisfaction by 20 units."
    )

    assert not numeric_context_matches(claim[0], evidence[0])


def test_numeric_context_matches_same_measurement_with_different_values():
    from src.verity.evidence import (
        extract_numeric_measurements,
        numeric_context_matches,
    )

    claim = extract_numeric_measurements(
        "The treatment increased blood pressure by 10 units."
    )
    evidence = extract_numeric_measurements(
        "The treatment increased blood pressure by 20 units."
    )

    assert numeric_context_matches(claim[0], evidence[0])


def test_numeric_matching_ignores_different_population():
    result = explain_classification(
        "Blood pressure in children increased by 10 units.",
        (
            "Blood pressure in adults increased by 20 units. "
            "Blood pressure in children increased by 15 units."
        ),
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert "10 units" in result["explanation"]
    assert "15 units" in result["explanation"]
    assert "20 units" not in result["explanation"]


def test_numeric_matching_accepts_same_population():
    result = explain_classification(
        "Blood pressure in children increased by 10 units.",
        "Blood pressure in children increased by 15 units.",
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert "10 units" in result["explanation"]
    assert "15 units" in result["explanation"]


def test_numerical_evidence_does_not_hide_mixed_findings():
    result = explain_classification(
        "Remote work improves productivity.",
        (
            "Remote work increases productivity by 10% "
            "in some teams. "
            "Remote work decreases productivity by 5% "
            "in other teams."
        ),
        "insufficient",
    )

    assert result["reason_code"] == "mixed_findings"
    assert "increases productivity" in result["explanation"].lower()
    assert "decreases productivity" in result["explanation"].lower()

def test_numerical_supporting_explanation_does_not_overstate_evidence():
    result = explain_classification(
        "The treatment reduces blood pressure by 10%.",
        "The treatment reduced blood pressure by 5%.",
        "supporting",
    )

    assert result["reason_code"] == "numerical_evidence"
    assert (
        "does not independently establish the classification"
        in result["explanation"]
    )