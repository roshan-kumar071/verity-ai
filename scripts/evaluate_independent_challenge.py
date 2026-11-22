import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from verity.evidence import classify_evidence

DATASET = ROOT / "tests" / "data" / "verity_independent_challenge_v1.json"


def main():
    with DATASET.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    correct = 0
    results = {
        "supporting": {"correct": 0, "total": 0},
        "contradicting": {"correct": 0, "total": 0},
        "insufficient": {"correct": 0, "total": 0},
    }

    print("\nINDEPENDENT CHALLENGE EVALUATION")
    print("=" * 65)

    for case in cases:
        expected = case["expected_label"]
        predicted = classify_evidence(
            case["claim"],
            case["evidence"],
        )

        passed = expected == predicted

        if passed:
            correct += 1
            results[expected]["correct"] += 1

        results[expected]["total"] += 1

        status = "PASS" if passed else "FAIL"

        print(
            f'{case["id"]} | {status} | '
            f'Expected: {expected} | Predicted: {predicted}'
        )

    total = len(cases)
    accuracy = (correct / total * 100) if total else 0

    print("\nSUMMARY")
    print("=" * 65)
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")

    print("\nLABEL-WISE RESULTS")

    for label, result in results.items():
        print(
            f'{label}: {result["correct"]}/{result["total"]} correct'
        )


if __name__ == "__main__":
    main()
