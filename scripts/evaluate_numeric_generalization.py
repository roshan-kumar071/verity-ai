import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.verity.evidence import classify_evidence

dataset_path = Path("tests/data/verity_numeric_generalization_v1.json")

with dataset_path.open(encoding="utf-8") as file:
    cases = json.load(file)

results = []

for case in cases:
    predicted = classify_evidence(
        case["claim"],
        case["evidence"]
    )

    expected = case["expected_label"]

    results.append({
        "id": case["id"],
        "expected": expected,
        "predicted": predicted,
        "correct": predicted == expected
    })

correct = sum(result["correct"] for result in results)
total = len(results)
accuracy = (correct / total) * 100

print("\nNUMERIC GENERALIZATION EVALUATION")
print("=" * 55)

for result in results:
    status = "PASS" if result["correct"] else "FAIL"
    print(
        f"{result['id']} | {status} | "
        f"Expected: {result['expected']} | "
        f"Predicted: {result['predicted']}"
    )

print("\nSUMMARY")
print("=" * 55)
print(f"Correct: {correct}/{total}")
print(f"Accuracy: {accuracy:.1f}%")

print("\nLABEL-WISE RESULTS")

for label in ["supporting", "contradicting", "insufficient"]:
    label_results = [
        result for result in results
        if result["expected"] == label
    ]

    label_correct = sum(
        result["correct"] for result in label_results
    )

    print(
        f"{label}: {label_correct}/{len(label_results)} correct"
    )
