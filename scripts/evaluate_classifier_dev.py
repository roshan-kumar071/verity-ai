import json
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.verity.evidence import classify_evidence


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "tests" / "data" / "verity_classifier_dev_v1.json"

LABELS = ["supporting", "contradicting", "insufficient"]


def load_dataset():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate():
    cases = load_dataset()

    expected = []
    predicted = []
    category_results = defaultdict(list)
    mistakes = []

    for case in cases:
        actual = case["expected_label"]
        prediction = classify_evidence(
            case["claim"],
            case["evidence"],
        )

        expected.append(actual)
        predicted.append(prediction)

        category_results[case["category"]].append(
            (actual, prediction)
        )

        if actual != prediction:
            mistakes.append({
                "case_id": case["case_id"],
                "category": case["category"],
                "claim": case["claim"],
                "evidence": case["evidence"],
                "expected": actual,
                "predicted": prediction,
            })

    print("\nVERITY AI - DEVELOPMENT BASELINE EVALUATION")
    print("=" * 55)

    print(f"Total cases: {len(cases)}")
    print(f"Correct predictions: {len(cases) - len(mistakes)}")
    print(f"Incorrect predictions: {len(mistakes)}")
    print(f"Accuracy: {accuracy_score(expected, predicted):.2%}")

    print("\nCLASSIFICATION REPORT")
    print("=" * 55)
    print(classification_report(
        expected,
        predicted,
        labels=LABELS,
        zero_division=0,
    ))

    print("CONFUSION MATRIX")
    print("=" * 55)
    print("Label order:", LABELS)
    print(confusion_matrix(expected, predicted, labels=LABELS))

    print("\nCATEGORY-WISE ACCURACY")
    print("=" * 55)

    for category, results in sorted(category_results.items()):
        correct = sum(actual == prediction for actual, prediction in results)
        print(
            f"{category}: {correct}/{len(results)} "
            f"({correct / len(results):.2%})"
        )

    print("\nMISCLASSIFIED CASES")
    print("=" * 55)

    if not mistakes:
        print("No misclassified cases.")
    else:
        for mistake in mistakes:
            print(f"\n{mistake['case_id']} ({mistake['category']})")
            print(f"Expected: {mistake['expected']}")
            print(f"Predicted: {mistake['predicted']}")
            print(f"Claim: {mistake['claim']}")
            print(f"Evidence: {mistake['evidence']}")


if __name__ == "__main__":
    evaluate()
