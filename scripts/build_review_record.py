
import json
from pathlib import Path
from collections import Counter
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tests" / "data"
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"

candidate_path = DATA / "verity_independent_holdout_v2_candidate.json"
review_path = DATA / "verity_label_review_v1.json"

with candidate_path.open(encoding="utf-8") as file:
    candidate = json.load(file)

with review_path.open(encoding="utf-8") as file:
    review = json.load(file)

review_map = {item["case_id"]: item for item in review["cases"]}
cases = candidate["cases"]

if len(cases) != 60 or len(review_map) != 60:
    raise ValueError("Expected exactly 60 candidate and review cases.")

if {case["id"] for case in cases} != set(review_map):
    raise ValueError("Candidate and review case IDs do not match.")

for case in cases:
    if case["expected_label"] != review_map[case["id"]]["proposed_label"]:
        raise ValueError(f"Label mismatch: {case['id']}")

lines = [
    "# Verity AI — Reviewed Dataset Record",
    "",
    f"Record generated: {date.today().isoformat()}",
    "",
    "## 1. Dataset identity",
    "",
    f"- Dataset: `{candidate['dataset_id']}`",
    "- Cases: 60",
    "- Status: Reviewed diagnostic candidate",
    "- Source: Original V1 holdout cases with reviewed labels",
    "- Original V1 holdout: Preserved unchanged",
    "",
    "## 2. Label distribution",
    ""
]

counts = Counter(case["expected_label"] for case in cases)

for label in ("supporting", "contradicting", "insufficient"):
    lines.append(f"- {label.title()}: {counts[label]}")

lines.extend([
    "",
    "## 3. Evaluation results",
    "",
    "| Classifier | Correct | Accuracy |",
    "|---|---:|---:|",
    "| Rule-based | 33/60 | 55.0% |",
    "| NLI DeBERTa | 45/60 | 75.0% |",
    "",
    "NLI scored 12 more correct cases than the rule-based baseline.",
    "",
    "These are diagnostic results on a revised-label candidate,",
    "not independent benchmark results or final production accuracy.",
    "NLI softmax scores are not calibrated probabilities.",
    "",
    "## 4. Review policy",
    "",
    "The following policy documents are included where available:",
    ""
])

policy_files = [
    DOCS / "evaluation_policy_v1.md",
    DOCS / "evaluation_policy_addendum_v1.md"
]

for policy_path in policy_files:
    if policy_path.exists():
        lines.extend([
            f"### {policy_path.name}",
            "",
            policy_path.read_text(encoding="utf-8").strip(),
            ""
        ])
    else:
        lines.extend([
            f"### {policy_path.name}",
            "",
            "Source policy file was not found during generation.",
            ""
        ])

lines.extend([
    "## 6. Case-by-case review record",
    "",
    "Each case retains its claim, evidence, original label, reviewed label,",
    "evidence rationale, review status and reviewer note.",
    ""
])

for case in cases:
    item = review_map[case["id"]]

    lines.extend([
        f"### {case['id']} — {case['category']}",
        "",
        f"**Claim:** {case['claim']}",
        "",
        f"**Evidence:** {case['evidence']}",
        "",
        f"**Original expected label:** {item['original_expected_label']}",
        "",
        f"**Reviewed label:** {item['proposed_label']}",
        "",
        f"**Review status:** {item['status']}",
        "",
        f"**Evidence rationale:** {case.get('rationale', 'Not recorded')}",
        "",
        f"**Review note:** {item.get('review_note') or 'No additional note recorded'}",
        ""
    ])

lines.extend([
    "## 6. Verification",
    "",
    "- Candidate and review case IDs match.",
    "- All 60 reviewed labels match the candidate labels.",
    "- Original V1 holdout was not modified by this generator.",
    "- This document is a record of the reviewed diagnostic dataset.",
    "",
    "## 7. Limitations",
    "",
    "- The candidate is derived from the original holdout cases.",
    "- Revised labels do not make it an independent test set.",
    "- Results must not be presented as final production accuracy.",
    "- Human review remains necessary for ambiguous evidence.",
    ""
])

REPORTS.mkdir(parents=True, exist_ok=True)

output_path = REPORTS / "verity_v2_reviewed_dataset_record.md"
output_path.write_text("\n".join(lines), encoding="utf-8")

print(f"Documentation created: {output_path}")
print(f"Cases documented: {len(cases)}")
print(f"Label mismatches: 0")
