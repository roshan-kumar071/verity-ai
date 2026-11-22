# Verity AI — Evidence Evaluation Policy v1

Status: Draft for review

## 1. Labels

### Supporting
Use when the evidence directly supports the claim and is
compatible with its relevant time, population, conditions,
outcome, and magnitude.

### Contradicting
Use when relevant evidence conflicts with the claim.
Absence of supporting evidence alone is not contradiction.

### Insufficient
Use when evidence is missing, incomplete, indirect, ambiguous,
or does not establish either support or contradiction.

## 2. Evaluation rules

1. Causation: Correlation and temporal sequence alone do not
   establish causation.
2. Time and numbers: Evidence from a different date or period
   does not automatically establish the claim's stated value.
3. Population: Evidence about one population does not
   automatically generalize to another.
4. Outcome: A related metric is not interchangeable with the
   outcome stated in the claim.
5. Conditions: Evidence under one condition does not establish
   a universal claim across untested conditions.
6. Magnitude: Qualitative strength words must be evaluated
   against the measured change and available context.
7. Scope: Evidence supports only the tested subject, outcome,
   and conditions unless broader applicability is established.
8. Confidence: Model scores are not guaranteed probabilities
   of correctness and must not replace evidence review.
9. Ambiguity: Borderline cases require human review and a
   recorded rationale.
10. Dataset integrity: Do not silently alter the original
    holdout labels or tune thresholds against the final holdout.

## 3. Evaluation process

- Preserve the original holdout dataset unchanged.
- Review ambiguous expected labels before treating them as
  ground truth.
- Record reviewed labels and rationales in a separate,
  versioned dataset.
- Compare models using the same reviewed evaluation cases.
- Report overall accuracy, per-label precision and recall,
  confusion matrix, and category-level results.
- Document limitations and unresolved disagreements.

## 4. Status and limitations

This is a proposed initial policy, not a claim that all
borderline cases have already been resolved. Human review
is required before finalizing ambiguous labels.
