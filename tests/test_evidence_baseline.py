
from verity.evidence import classify_evidence


CASES = [
    {
        "name": "clear_support",
        "claim": "Remote work improves employee productivity.",
        "source": "Remote work improves employee productivity.",
        "expected": "supporting",
    },
    {
        "name": "clear_contradiction",
        "claim": "Remote work improves employee productivity.",
        "source": "Remote work reduces employee productivity.",
        "expected": "contradicting",
    },
    {
        "name": "unrelated_evidence",
        "claim": "Remote work improves employee productivity.",
        "source": "Ocean temperatures affect coral reef growth.",
        "expected": "insufficient",
    },
    {
        "name": "uncertain_evidence",
        "claim": "Remote work improves employee productivity.",
        "source": "Remote work may improve employee productivity.",
        "expected": "insufficient",
    },
    {
        "name": "mixed_findings",
        "claim": "Remote work improves employee productivity.",
        "source": (
            "Remote work improves productivity for focused tasks. "
            "Remote work reduces productivity for collaborative tasks."
        ),
        "expected": "insufficient",
    },
    {
        "name": "wrong_subject",
        "claim": "Remote work improves employee productivity.",
        "source": "Office lighting improves employee productivity.",
        "expected": "insufficient",
    },
    
    {
        "name": "negated_claim",
        "claim": "Remote work improves employee productivity.",
        "source": "Remote work does not improve employee productivity.",
        "expected": "insufficient",
    },
    {
        "name": "different_subject_health",
        "claim": "Regular exercise improves sleep quality.",
        "source": "A balanced diet improves cardiovascular health.",
        "expected": "insufficient",
    },
    {
        "name": "different_subject_technology",
        "claim": "Using SSDs improves computer startup speed.",
        "source": "Adding more RAM improves multitasking performance.",
        "expected": "insufficient",
    },
    {
        "name": "different_subject_education",
        "claim": "Smaller class sizes improve student learning outcomes.",
        "source": "Teacher training improves classroom management.",
        "expected": "insufficient",
    },
    {
        "name": "number_mismatch",
        "claim": "The treatment reduced symptoms by 40 percent.",
        "source": "The treatment reduced symptoms by 10 percent.",
        "expected": "insufficient",
    },
    {
        "name": "partial_support",
        "claim": "Remote work improves productivity and employee satisfaction.",
        "source": "Remote work improves productivity.",
        "expected": "insufficient",
    },
    
    {
        "name": "percentage_format_mismatch",
        "claim": "Remote work improves productivity by 40 percent.",
        "source": "Remote work improves productivity by 10 percent.",
        "expected": "insufficient",
    },
    {
        "name": "same_number_support",
        "claim": "The treatment reduced symptoms by 40 percent.",
        "source": "The treatment reduced symptoms by 40 percent.",
        "expected": "supporting",
    },
    {
        "name": "contradictory_sources",
        "claim": "Remote work improves employee productivity.",
        "source": (
            "Remote work improves employee productivity. "
            "Remote work reduces employee productivity."
        ),
        "expected": "insufficient",
    },
    {
        "name": "claim_not_covered",
        "claim": "Remote work improves productivity and satisfaction.",
        "source": "Remote work improves productivity.",
        "expected": "insufficient",
    },
    {
        "name": "same_topic_different_outcome",
        "claim": "Regular exercise improves sleep quality.",
        "source": "Regular exercise improves cardiovascular health.",
        "expected": "insufficient",
    },
    {
        "name": "uncertain_contradiction",
        "claim": "Remote work improves employee productivity.",
        "source": "Remote work may reduce employee productivity.",
        "expected": "insufficient",
    },
    {
        "name": "different_number_support",
        "claim": "The treatment reduced symptoms by 40 percent.",
        "source": "The treatment reduced symptoms by 40 percent.",
        "expected": "supporting",
    },
    {
        "name": "opposite_direction",
        "claim": "Remote work improves employee productivity.",
        "source": "Remote work reduces employee productivity.",
        "expected": "contradicting",
    },

]


def test_rule_based_baseline_cases():
    labels = ["supporting", "contradicting", "insufficient"]
    results = []
    correct = 0

    # Rows = expected labels; columns = predicted labels.
    matrix = {
        actual_label: {predicted_label: 0 for predicted_label in labels}
        for actual_label in labels
    }

    for case in CASES:
        expected = case["expected"]
        predicted = classify_evidence(case["claim"], case["source"])
        passed = predicted == expected

        if passed:
            correct += 1

        if expected in matrix and predicted in labels:
            matrix[expected][predicted] += 1

        results.append({
            "name": case["name"],
            "expected": expected,
            "predicted": predicted,
            "passed": passed,
        })

    total = len(CASES)
    accuracy = correct / total if total else 0

    print("\n" + "=" * 60)
    print("VERITY AI — CLASSIFIER EVALUATION")
    print("=" * 60)

    print("\nCONFUSION MATRIX")
    print(f'{"Expected \\ Predicted":<22}' + "".join(
        f"{label:>16}" for label in labels
    ))

    for expected in labels:
        print(
            f"{expected:<22}"
            + "".join(f"{matrix[expected][predicted]:>16}" for predicted in labels)
        )

    print("\nPRECISION AND RECALL")
    for label in labels:
        true_positive = matrix[label][label]
        predicted_total = sum(matrix[actual][label] for actual in labels)
        actual_total = sum(matrix[label].values())

        precision = (
            true_positive / predicted_total
            if predicted_total else 0
        )
        recall = (
            true_positive / actual_total
            if actual_total else 0
        )

        print(
            f"{label}: precision={precision:.1%}, "
            f"recall={recall:.1%} "
            f"(actual cases={actual_total}, predictions={predicted_total})"
        )

    print("\nOVERALL")
    print(f"Cases: {total}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {total - correct}")
    print(f"Accuracy: {accuracy:.1%}")

    failures = [result for result in results if not result["passed"]]
    print("\nFAILED CASES")

    if failures:
        for result in failures:
            print(
                f'- {result["name"]}: expected={result["expected"]}, '
                f'predicted={result["predicted"]}'
            )
    else:
        print("None")

    print("=" * 60)

    assert correct == total, f"{total - correct} evaluation case(s) failed."

