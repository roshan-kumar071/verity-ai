import json
from collections import Counter, defaultdict
from pathlib import Path

from verity.evidence import classify_evidence


ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = ROOT / "tests" / "data" / "verity_independent_holdout_v2_candidate.json"
LABELS = ("supporting", "contradicting", "insufficient")


def main():
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    cases = dataset["cases"]
    confusion = {actual: Counter() for actual in LABELS}
    category_stats = defaultdict(lambda: {"total": 0, "correct": 0})
    failures = []
    predictions = Counter()

    for case in cases:
        expected = case["expected_label"]
        predicted = classify_evidence(case["claim"], case["evidence"])

        if expected not in LABELS:
            raise ValueError(f"Invalid expected label in {case['id']}: {expected}")
        if predicted not in LABELS:
            raise ValueError(f"Invalid predicted label for {case['id']}: {predicted}")

        confusion[expected][predicted] += 1
        predictions[predicted] += 1

        category = case["category"]
        category_stats[category]["total"] += 1
        if predicted == expected:
            category_stats[category]["correct"] += 1
        else:
            failures.append((case, predicted))

    total = len(cases)
    correct = total - len(failures)

    print(f"Dataset: {dataset['dataset_id']}")
    print(f"Cases: {total}")
    print("\nCONFUSION MATRIX")
    print(f"{'Expected \\\\ Predicted':<24}" + "".join(f"{label:>17}" for label in LABELS))
    for actual in LABELS:
        print(f"{actual:<24}" + "".join(f"{confusion[actual][label]:>17}" for label in LABELS))

    print("\nPRECISION AND RECALL")
    for label in LABELS:
        true_positive = confusion[label][label]
        predicted_count = predictions[label]
        actual_count = sum(confusion[label].values())
        precision = true_positive / predicted_count if predicted_count else 0
        recall = true_positive / actual_count if actual_count else 0
        print(
            f"{label}: precision={precision:.1%}, recall={recall:.1%} "
            f"(actual={actual_count}, predicted={predicted_count})"
        )

    print("\nCATEGORY RESULTS")
    for category in sorted(category_stats):
        stats = category_stats[category]
        accuracy = stats["correct"] / stats["total"] if stats["total"] else 0
        print(f"{category}: {stats['correct']}/{stats['total']} correct ({accuracy:.1%})")

    print("\nOVERALL")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {correct / total:.1%}" if total else "Accuracy: N/A")

    print("\nMISCLASSIFIED CASES")
    if not failures:
        print("None")
    else:
        for case, predicted in failures:
            print(f"\n{case['id']} [{case['category']}]")
            print(f"Expected: {case['expected_label']} | Predicted: {predicted}")
            print(f"Claim: {case['claim']}")
            print(f"Evidence: {case['evidence']}")
            print(f"Rationale: {case['rationale']}")


if __name__ == "__main__":
    main()
