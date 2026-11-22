
import csv
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from verity.evidence import classify_evidence

DATASET_PATH = ROOT / "tests" / "data" / "verity_independent_holdout_v2_candidate.json"
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"
REPORT_PATH = ROOT / "reports" / "nli_v2_candidate_predictions.csv"

LABELS = ("supporting", "contradicting", "insufficient")

MODEL_TO_VERITY = {
    "entailment": "supporting",
    "contradiction": "contradicting",
    "neutral": "insufficient",
}


def evaluate_predictions(cases, predictions, title):
    confusion = {label: Counter() for label in LABELS}
    predicted_counts = Counter()
    category_stats = defaultdict(lambda: {"total": 0, "correct": 0})
    failures = []

    for case, predicted in zip(cases, predictions):
        expected = case["expected_label"]
        if expected not in LABELS or predicted not in LABELS:
            raise ValueError(f"Unexpected label in case {case['id']}")

        confusion[expected][predicted] += 1
        predicted_counts[predicted] += 1

        stats = category_stats[case["category"]]
        stats["total"] += 1
        if expected == predicted:
            stats["correct"] += 1
        else:
            failures.append((case, predicted))

    correct = sum(confusion[label][label] for label in LABELS)
    total = len(cases)

    print(f"\n{'=' * 18} {title} {'=' * 18}")
    print(f"Accuracy: {correct}/{total} = {correct / total:.1%}")
    print("\nCONFUSION MATRIX (expected rows, predicted columns)")
    print(f"{'Expected \\\\ Predicted':<22}" + "".join(
        f"{x:>17}" for x in LABELS
    ))

    for actual in LABELS:
        print(f"{actual:<22}" + "".join(
            f"{confusion[actual][pred]:>17}" for pred in LABELS
        ))

    print("\nPRECISION / RECALL")
    for label in LABELS:
        tp = confusion[label][label]
        actual = sum(confusion[label].values())
        predicted_count = predicted_counts[label]
        precision = tp / predicted_count if predicted_count else 0
        recall = tp / actual if actual else 0
        print(
            f"{label}: precision={precision:.1%}, recall={recall:.1%} "
            f"(actual={actual}, predicted={predicted_count})"
        )

    print("\nCATEGORY RESULTS")
    for category in sorted(category_stats):
        stats = category_stats[category]
        accuracy = stats["correct"] / stats["total"]
        print(f"{category}: {stats['correct']}/{stats['total']} ({accuracy:.1%})")

    print("\nMISCLASSIFIED CASES")
    for case, predicted in failures:
        print(
            f"{case['id']} [{case['category']}] "
            f"expected={case['expected_label']} predicted={predicted}"
        )


def main():
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    cases = dataset["cases"]
    if not cases:
        raise ValueError("Holdout dataset contains no cases.")

    print(f"Dataset: {dataset['dataset_id']} | cases: {len(cases)}")
    print(f"Device: CPU | Model: {MODEL_NAME}")
    print("Loading tokenizer and model...")

    load_start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    model.to("cpu")
    load_seconds = time.perf_counter() - load_start

    id2label = {
        int(key): value.lower()
        for key, value in model.config.id2label.items()
    }
    print("Model labels:", id2label)

    if set(id2label.values()) != set(MODEL_TO_VERITY):
        raise ValueError(f"Unexpected model label mapping: {id2label}")

    predictions = []
    score_rows = []
    inference_start = time.perf_counter()

    # Evidence = premise; claim = hypothesis.
    with torch.inference_mode():
        for start in range(0, len(cases), 8):
            batch = cases[start:start + 8]
            encoded = tokenizer(
                [case["evidence"] for case in batch],
                [case["claim"] for case in batch],
                padding=True,
                truncation=True,
                max_length=256,
                return_tensors="pt",
            )

            logits = model(**encoded).logits
            probabilities = torch.softmax(logits, dim=-1)
            best_ids = probabilities.argmax(dim=-1).tolist()
            probability_rows = probabilities.tolist()

            for case, best_id, probability_row in zip(
                batch, best_ids, probability_rows
            ):
                raw_label = id2label[best_id]
                predicted = MODEL_TO_VERITY[raw_label]
                scores = {
                    MODEL_TO_VERITY[id2label[index]]: float(score)
                    for index, score in enumerate(probability_row)
                }

                predictions.append(predicted)
                score_rows.append({
                    "case": case,
                    "predicted": predicted,
                    "scores": scores,
                })

    inference_seconds = time.perf_counter() - inference_start

    print(f"Model load time: {load_seconds:.2f} seconds")
    print(f"Inference time for {len(cases)} cases: {inference_seconds:.2f} seconds")
    print(
        "Average inference time per case: "
        f"{inference_seconds / len(cases):.3f} seconds"
    )

    evaluate_predictions(cases, predictions, "NLI MODEL")

    # Save per-case predictions and all three softmax scores.
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", newline="", encoding="utf-8-sig") as file:
        fieldnames = [
            "case_id",
            "category",
            "claim",
            "evidence",
            "expected_label",
            "predicted_label",
            "correct",
            "supporting_score",
            "contradicting_score",
            "insufficient_score",
            "top_score",
            "second_score",
            "score_margin",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in score_rows:
            case = row["case"]
            scores = row["scores"]
            ranked_scores = sorted(scores.values(), reverse=True)

            writer.writerow({
                "case_id": case["id"],
                "category": case["category"],
                "claim": case["claim"],
                "evidence": case["evidence"],
                "expected_label": case["expected_label"],
                "predicted_label": row["predicted"],
                "correct": case["expected_label"] == row["predicted"],
                "supporting_score": f"{scores['supporting']:.6f}",
                "contradicting_score": f"{scores['contradicting']:.6f}",
                "insufficient_score": f"{scores['insufficient']:.6f}",
                "top_score": f"{ranked_scores[0]:.6f}",
                "second_score": f"{ranked_scores[1]:.6f}",
                "score_margin": f"{ranked_scores[0] - ranked_scores[1]:.6f}",
            })

    print(f"\nConfidence report saved to: {REPORT_PATH}")

    print("\nMISCLASSIFIED NLI CASES WITH SCORES")
    for row in score_rows:
        case = row["case"]
        if case["expected_label"] == row["predicted"]:
            continue

        scores = row["scores"]
        print(
            f"{case['id']} [{case['category']}] "
            f"expected={case['expected_label']} "
            f"predicted={row['predicted']} | "
            f"supporting={scores['supporting']:.3f}, "
            f"contradicting={scores['contradicting']:.3f}, "
            f"insufficient={scores['insufficient']:.3f}"
        )

    baseline_predictions = [
        classify_evidence(case["claim"], case["evidence"])
        for case in cases
    ]
    evaluate_predictions(cases, baseline_predictions, "EXISTING RULE-BASED BASELINE")

    print("\nNote: Holdout labels are provisional and need human review.")
    print("Softmax scores are model confidence estimates, not guaranteed probabilities.")
    print("No production classifier code or holdout data was modified.")


if __name__ == "__main__":
    main()
