from verity.evidence import classify_evidence


REALWORLD_CASES = [
    {
        "name": "paraphrased_support",
        "claim": "Regular exercise improves sleep quality.",
        "source": "People who exercise regularly tend to have better sleep quality.",
        "expected": "supporting",
    },
    {
        "name": "association_not_causation",
        "claim": "Eating blueberries improves memory.",
        "source": "Blueberry consumption is associated with better memory scores.",
        "expected": "insufficient",
    },
    {
        "name": "unrelated_negation",
        "claim": "Regular exercise improves sleep quality.",
        "source": "Regular exercise improves sleep quality, but the study did not measure blood pressure.",
        "expected": "insufficient",
    },
    {
        "name": "percentage_word_format",
        "claim": "The treatment reduced symptoms by 40 percent.",
        "source": "The treatment reduced symptoms by 40 percent.",
        "expected": "supporting",
    },
    {
        "name": "different_time_period",
        "claim": "The program increased sales in 2025.",
        "source": "The program increased sales in 2024.",
        "expected": "insufficient",
    },
    {
        "name": "small_effect_vs_large_claim",
        "claim": "The intervention dramatically improves productivity.",
        "source": "The intervention slightly improves productivity.",
        "expected": "insufficient",
    },
    {
        "name": "explicit_opposite_result",
        "claim": "The new policy increases employment.",
        "source": "The new policy decreases employment.",
        "expected": "contradicting",
    },
    {
        "name": "different_measure_same_topic",
        "claim": "The app improves user retention.",
        "source": "The app improves user satisfaction.",
        "expected": "insufficient",
    },
    {
        "name": "conditional_effect",
        "claim": "Remote work improves employee productivity.",
        "source": "Remote work improves employee productivity only when employees have a quiet workspace.",
        "expected": "insufficient",
    },
    {
        "name": "clear_direct_support",
        "claim": "The new insulation reduces household energy use.",
        "source": "The new insulation reduces household energy use.",
        "expected": "supporting",
    },
]


def test_realworld_evaluation_cases():
    labels = {"supporting", "contradicting", "insufficient"}
    failures = []

    for case in REALWORLD_CASES:
        predicted = classify_evidence(case["claim"], case["source"])

        if predicted not in labels or predicted != case["expected"]:
            failures.append(
                f'{case["name"]}: expected={case["expected"]}, '
                f'predicted={predicted}'
            )

    print("\nVERITY AI — REAL-WORLD CHALLENGE SET")
    print(f"Cases: {len(REALWORLD_CASES)}")
    print(f"Correct: {len(REALWORLD_CASES) - len(failures)}")
    print(f"Incorrect: {len(failures)}")
    print(f"Accuracy: {(len(REALWORLD_CASES) - len(failures)) / len(REALWORLD_CASES):.1%}")

    for failure in failures:
        print(f"- {failure}")

    assert not failures, (
        f"{len(failures)} real-world evaluation case(s) failed."
    )



TARGETED_FAILURE_CASES = [
    {
        "name": "magnitude_mismatch",
        "claim": "The intervention dramatically improves productivity.",
        "source": "The intervention slightly improves productivity.",
        "expected": "insufficient",
    },
    {
        "name": "outcome_mismatch",
        "claim": "The app improves user retention.",
        "source": "The app improves user satisfaction.",
        "expected": "insufficient",
    },
    {
        "name": "conditional_evidence_for_unconditional_claim",
        "claim": "Remote work improves employee productivity.",
        "source": (
            "Remote work improves employee productivity only "
            "when employees have a quiet workspace."
        ),
        "expected": "insufficient",
    },
]


def test_targeted_failure_cases():
    failures = []

    for case in TARGETED_FAILURE_CASES:
        predicted = classify_evidence(case["claim"], case["source"])

        if predicted != case["expected"]:
            failures.append(
                f'{case["name"]}: expected={case["expected"]}, '
                f'predicted={predicted}'
            )

    assert not failures, "\n".join(failures)
