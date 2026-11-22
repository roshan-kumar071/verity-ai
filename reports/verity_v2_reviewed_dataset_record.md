# Verity AI — Reviewed Dataset Record

Record generated: 2026-11-22

## 1. Dataset identity

- Dataset: `verity_independent_holdout_v2_candidate`
- Cases: 60
- Status: Reviewed diagnostic candidate
- Source: Original V1 holdout cases with reviewed labels
- Original V1 holdout: Preserved unchanged

## 2. Label distribution

- Supporting: 15
- Contradicting: 14
- Insufficient: 31

## 3. Evaluation results

| Classifier | Correct | Accuracy |
|---|---:|---:|
| Rule-based | 33/60 | 55.0% |
| NLI DeBERTa | 45/60 | 75.0% |

NLI scored 12 more correct cases than the rule-based baseline.

These are diagnostic results on a revised-label candidate,
not independent benchmark results or final production accuracy.
NLI softmax scores are not calibrated probabilities.

## 4. Review policy

The following policy documents are included where available:

### evaluation_policy_v1.md

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

### evaluation_policy_addendum_v1.md

# Evaluation Policy Addendum v1

Status: Proposed; human review required before treating revised labels as final.

## 1. Causal claims
A temporal association, before-and-after change, or observational correlation
alone does not establish causation. A causal claim requires evidence that
supports the causal relationship, not merely a change in the same outcome.

## 2. Broad claims and measured outcomes
Evidence for one specific metric supports that metric only. It must not
automatically be treated as evidence for a broader claim such as "improved
outcomes" unless the source establishes that broader scope.

## 3. Attributed causal conclusions
A source's explicit investigator attribution may be retained as provisional
supporting evidence. If the method or strength of that attribution is
unavailable, record the limitation and do not treat the label as confirmed.

## 4. Ambiguous cases
Cases whose labels depend on interpretation or missing methodology must remain
marked for human confirmation. Proposed labels are not final ground truth.

## 5. Evaluation safeguards
Keep the original holdout unchanged. Record proposed revisions separately.
Do not tune model thresholds against the same holdout used for final reporting.
Re-evaluate only against a clearly versioned dataset with documented labels.

## 6. Case-by-case review record

Each case retains its claim, evidence, original label, reviewed label,
evidence rationale, review status and reviewer note.

### H001 — paraphrase

**Claim:** The city’s new bike lanes reduced car traffic downtown.

**Evidence:** After protected cycling lanes opened, downtown vehicle counts fell by 12%.

**Original expected label:** supporting

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Downtown vehicle counts fell by 12% after protected bike lanes opened. The before-and-after association alone does not establish that the bike lanes caused the reduction.

**Review note:** Downtown vehicle counts fell by 12% after protected bike lanes opened. The before-and-after association alone does not establish that the bike lanes caused the reduction.

### H002 — paraphrase

**Claim:** The city’s new bike lanes reduced car traffic downtown.

**Evidence:** Cycling-lane construction finished in June, and downtown vehicle counts were measured in July.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The evidence gives timing but no direction of traffic change or causal evidence.

**Review note:** The evidence gives timing but no direction of traffic change or causal evidence.

### H003 — paraphrase

**Claim:** Remote work improved employee satisfaction.

**Evidence:** Employees working from home reported higher satisfaction scores than before the policy.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** Higher satisfaction scores among remote workers match the claimed outcome.

**Review note:** Higher satisfaction scores among remote workers match the claimed outcome.

### H004 — paraphrase

**Claim:** Remote work improved employee satisfaction.

**Evidence:** Employees said they liked the flexibility of remote work.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Positive comments about flexibility do not establish an overall satisfaction improvement.

**Review note:** Positive comments about flexibility do not establish an overall satisfaction improvement.

### H005 — paraphrase

**Claim:** The new tutoring program helped students learn mathematics.

**Evidence:** Students enrolled in the tutoring program achieved higher mathematics test scores than their previous scores.

**Original expected label:** supporting

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Before-and-after score improvement alone does not establish that the tutoring program caused the improvement.

**Review note:** Before-and-after score improvement alone does not establish that the tutoring program caused the improvement.

### H006 — paraphrase

**Claim:** The new tutoring program helped students learn mathematics.

**Evidence:** The tutoring program was offered to students who were already struggling in mathematics.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The evidence describes program eligibility or recipients, not learning outcomes.

**Review note:** The evidence describes program eligibility or recipients, not learning outcomes.

### H007 — paraphrase

**Claim:** The medication shortened recovery time.

**Evidence:** Patients receiving the medication recovered in fewer days on average.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** Fewer recovery days directly match shorter recovery time.

**Review note:** Fewer recovery days directly match shorter recovery time.

### H008 — paraphrase

**Claim:** The medication shortened recovery time.

**Evidence:** Most patients recovered after taking the medication.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Recovery after medication does not show that recovery was faster.

**Review note:** Recovery after medication does not show that recovery was faster.

### H009 — paraphrase

**Claim:** The policy lowered household energy use.

**Evidence:** Average household electricity consumption was lower after the policy began.

**Original expected label:** supporting

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Average household electricity consumption was lower after the policy began. The temporal association alone does not establish that the policy caused the reduction.

**Review note:** Average household electricity consumption was lower after the policy began. The temporal association alone does not establish that the policy caused the reduction.

### H010 — paraphrase

**Claim:** The policy lowered household energy use.

**Evidence:** The policy was designed to encourage households to conserve electricity.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The policy's stated aim does not demonstrate an actual reduction in energy use.

**Review note:** The policy's stated aim does not demonstrate an actual reduction in energy use.

### H011 — causation

**Claim:** Daily exercise prevents depression.

**Evidence:** People who exercised daily had lower rates of depression in an observational survey.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** An observational association does not establish that exercise prevents depression.

**Review note:** An observational association does not establish that exercise prevents depression.

### H012 — causation

**Claim:** The new app caused workers to become more productive.

**Evidence:** Workers using the app completed more tasks, but the study did not control for prior productivity.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Prior productivity was not controlled, leaving alternative explanations.

**Review note:** Prior productivity was not controlled, leaving alternative explanations.

### H013 — causation

**Claim:** Eating breakfast increases exam scores.

**Evidence:** Students who ate breakfast scored higher, although breakfast habits were not randomly assigned.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The observational comparison does not establish that breakfast caused higher exam scores.

**Review note:** The observational comparison does not establish that breakfast caused higher exam scores.

### H014 — causation

**Claim:** The factory closure reduced local asthma cases.

**Evidence:** Asthma cases declined after the factory closed, and investigators attributed the decline to reduced emissions.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** Investigators explicitly attributed the decline in asthma cases to reduced emissions after the factory closure. Retained provisionally; the attribution method and strength are not specified.

**Review note:** Investigators explicitly attributed the decline in asthma cases to reduced emissions after the factory closure. Retained provisionally; the attribution method and strength are not specified.

### H015 — causation

**Claim:** Social media use causes anxiety in teenagers.

**Evidence:** A survey found that teenagers with higher social media use also reported more anxiety.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Correlation alone does not establish causation.

**Review note:** Correlation alone does not establish causation.

### H016 — causation

**Claim:** The training course improved sales.

**Evidence:** Sales rose during the quarter in which the course was introduced, while advertising spending also increased substantially.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Advertising spending also increased, so the course's independent effect is unclear.

**Review note:** Advertising spending also increased, so the course's independent effect is unclear.

### H017 — causation

**Claim:** Installing insulation lowered heating costs.

**Evidence:** A controlled comparison found homes with the new insulation used less heating energy than similar homes without it.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** A controlled comparison of similar homes supports lower heating energy use with insulation.

**Review note:** A controlled comparison of similar homes supports lower heating energy use with insulation.

### H018 — causation

**Claim:** The tax increase caused restaurant closures.

**Evidence:** Several restaurants closed after the tax increase, but the report did not examine why they closed.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Temporal sequence alone does not establish causation.

**Review note:** Temporal sequence alone does not establish causation.

### H019 — numeric_mismatch

**Claim:** The project reduced costs by 20%.

**Evidence:** The audited report found that project costs fell by 20% compared with the previous year.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** The 20% decrease matches the stated comparison.

**Review note:** The 20% decrease matches the stated comparison.

### H020 — numeric_mismatch

**Claim:** The project reduced costs by 20%.

**Evidence:** The audited report found that project costs fell by 12% compared with the previous year.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** The evidence reports a 12% decrease rather than 20%.

**Review note:** The evidence reports a 12% decrease rather than 20%.

### H021 — numeric_mismatch

**Claim:** The town’s population reached 50,000 in 2024.

**Evidence:** The census recorded 50,000 residents in the town in 2024.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** Population, value, location, and year match.

**Review note:** Population, value, location, and year match.

### H022 — numeric_mismatch

**Claim:** The town’s population reached 50,000 in 2024.

**Evidence:** The census recorded 50,000 residents in the town in 2022.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The evidence refers to 2022, not 2024.

**Review note:** The evidence refers to 2022, not 2024.

### H023 — numeric_mismatch

**Claim:** The battery lasts 10 hours on one charge.

**Evidence:** In the standardized test, the battery lasted 8 hours on one charge.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** The standardized test reports 8 hours rather than 10.

**Review note:** The standardized test reports 8 hours rather than 10.

### H024 — numeric_mismatch

**Claim:** The battery lasts 10 hours on one charge.

**Evidence:** The battery was tested at 10 hours of continuous video playback.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** A 10-hour test duration does not establish 10 hours of actual battery runtime.

**Review note:** A 10-hour test duration does not establish 10 hours of actual battery runtime.

### H025 — numeric_mismatch

**Claim:** Revenue increased from $2 million to $3 million.

**Evidence:** Annual revenue rose from $2 million to $3 million.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** The revenue values match: $2 million to $3 million.

**Review note:** The revenue values match: $2 million to $3 million.

### H026 — numeric_mismatch

**Claim:** Revenue increased from $2 million to $3 million.

**Evidence:** Annual revenue rose from $2 million to $2.5 million.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** The evidence reports $2.5 million rather than $3 million.

**Review note:** The evidence reports $2.5 million rather than $3 million.

### H027 — negation

**Claim:** The trial found that the treatment reduced pain.

**Evidence:** The trial found no meaningful reduction in pain compared with placebo.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** Evidence reports no meaningful reduction, contrary to the claim.

**Review note:** Evidence reports no meaningful reduction, contrary to the claim.

### H028 — negation

**Claim:** The trial found that the treatment reduced pain.

**Evidence:** The trial found a meaningful reduction in pain compared with placebo.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** Evidence directly reports a meaningful reduction in pain.

**Review note:** Evidence directly reports a meaningful reduction in pain.

### H029 — negation

**Claim:** The company did not miss its delivery target.

**Evidence:** The company missed its delivery target by two days.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** Evidence says the company missed its delivery target.

**Review note:** Evidence says the company missed its delivery target.

### H030 — negation

**Claim:** The company did not miss its delivery target.

**Evidence:** The company delivered all orders within the target window.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** All orders arrived within the target window.

**Review note:** All orders arrived within the target window.

### H031 — negation

**Claim:** The update did not fix the security vulnerability.

**Evidence:** The vulnerability remained exploitable after the update.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** The vulnerability remained exploitable after the update.

**Review note:** The vulnerability remained exploitable after the update.

### H032 — negation

**Claim:** The update did not fix the security vulnerability.

**Evidence:** Testing confirmed that the update eliminated the vulnerability.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** Evidence says the update eliminated the vulnerability.

**Review note:** Evidence says the update eliminated the vulnerability.

### H033 — negation

**Claim:** The school’s absence rate did not increase.

**Evidence:** The absence rate stayed at 4% in both terms.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** The unchanged 4% absence rate supports no increase.

**Review note:** The unchanged 4% absence rate supports no increase.

### H034 — negation

**Claim:** The school’s absence rate did not increase.

**Evidence:** The absence rate rose from 4% to 6%.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** The absence rate increased from 4% to 6%.

**Review note:** The absence rate increased from 4% to 6%.

### H035 — population_outcome

**Claim:** The program improved outcomes for adults over 65.

**Evidence:** Among adults aged 18–30, completion rates improved after the program.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Evidence concerns ages 18-30, not adults over 65.

**Review note:** Evidence concerns ages 18-30, not adults over 65.

### H036 — population_outcome

**Claim:** The program improved outcomes for adults over 65.

**Evidence:** Among adults aged 65 and older, completion rates improved after the program.

**Original expected label:** supporting

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The evidence measures completion rates among adults aged 65+, while the claim concerns broader outcomes. The measured metric does not establish the broader claim.

**Review note:** The evidence measures completion rates among adults aged 65+, while the claim concerns broader outcomes. The measured metric does not establish the broader claim.

### H037 — population_outcome

**Claim:** The policy increased employment in rural areas.

**Evidence:** Urban employment rose by 3% after the policy began.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Urban employment data does not establish rural employment.

**Review note:** Urban employment data does not establish rural employment.

### H038 — population_outcome

**Claim:** The policy increased employment in rural areas.

**Evidence:** Rural employment fell by 3% after the policy began.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** Rural employment fell by 3%, opposite to the claimed increase.

**Review note:** Rural employment fell by 3%, opposite to the claimed increase.

### H039 — population_outcome

**Claim:** The supplement improved sleep quality.

**Evidence:** Participants reported better sleep quality after using the supplement.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** Participants reported better sleep quality, matching the claimed outcome.

**Review note:** Participants reported better sleep quality, matching the claimed outcome.

### H040 — population_outcome

**Claim:** The supplement improved sleep quality.

**Evidence:** Participants reported falling asleep faster, but overall sleep quality was not measured.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Falling asleep faster is related to, but not equivalent to, overall sleep quality.

**Review note:** Falling asleep faster is related to, but not equivalent to, overall sleep quality.

### H041 — population_outcome

**Claim:** The redesign increased customer retention.

**Evidence:** The redesign increased the number of first-time purchases.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** First-time purchases measure acquisition, not retention.

**Review note:** First-time purchases measure acquisition, not retention.

### H042 — population_outcome

**Claim:** The redesign increased customer retention.

**Evidence:** The share of customers returning within 90 days increased after the redesign.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** The share of customers returning within 90 days increased, directly supporting improved retention.

**Review note:** The share of customers returning within 90 days increased, directly supporting improved retention.

### H043 — conditional_scope

**Claim:** The device works reliably in all weather conditions.

**Evidence:** The device operates reliably in dry weather, but its performance in rain was not tested.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Dry-weather performance does not establish all-weather reliability.

**Review note:** Dry-weather performance does not establish all-weather reliability.

### H044 — conditional_scope

**Claim:** The device works reliably in all weather conditions.

**Evidence:** The device failed during heavy rain testing.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** Failure during heavy rain conflicts with reliable operation in all weather conditions.

**Review note:** Failure during heavy rain conflicts with reliable operation in all weather conditions.

### H045 — conditional_scope

**Claim:** The benefit applies to every applicant.

**Evidence:** Applicants receive the benefit only if their income is below the eligibility threshold.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** The benefit has an income eligibility condition, so it does not apply to every applicant.

**Review note:** The benefit has an income eligibility condition, so it does not apply to every applicant.

### H046 — conditional_scope

**Claim:** The benefit applies to eligible low-income applicants.

**Evidence:** Applicants receive the benefit only if their income is below the eligibility threshold and other criteria are met.

**Original expected label:** supporting

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Eligibility conditions do not establish that an applicant actually applied or that every eligible applicant received the benefit.

**Review note:** Eligibility conditions do not establish that an applicant actually applied or that every eligible applicant received the benefit.

### H047 — conditional_scope

**Claim:** The treatment is effective regardless of age.

**Evidence:** The treatment was effective in adults, but effectiveness in children remains unknown.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Adult effectiveness does not establish effectiveness in children.

**Review note:** Adult effectiveness does not establish effectiveness in children.

### H048 — conditional_scope

**Claim:** The service is available every day.

**Evidence:** The service is available on weekdays only.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** Weekday-only availability conflicts with availability every day.

**Review note:** Weekday-only availability conflicts with availability every day.

### H049 — magnitude

**Claim:** The intervention dramatically improved test scores.

**Evidence:** Average test scores increased slightly after the intervention.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** A slight increase does not match the claim of a dramatic improvement.

**Review note:** A slight increase does not match the claim of a dramatic improvement.

### H050 — magnitude

**Claim:** The intervention slightly improved test scores.

**Evidence:** Average test scores increased modestly after the intervention.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** A modest increase is consistent with a slight improvement.

**Review note:** A modest increase is consistent with a slight improvement.

### H051 — magnitude

**Claim:** The product substantially reduced noise.

**Evidence:** Noise levels fell by 1% in the measured room.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** A 1% reduction appears inconsistent with 'substantially reduced'.

**Review note:** A 1% reduction appears inconsistent with 'substantially reduced'.

### H052 — magnitude

**Claim:** The product slightly reduced noise.

**Evidence:** Measured noise levels fell by 1%.

**Original expected label:** supporting

**Reviewed label:** supporting

**Review status:** provisional_retain

**Evidence rationale:** A measured 1% reduction matches the claim of a slight reduction.

**Review note:** A measured 1% reduction matches the claim of a slight reduction.

### H053 — magnitude

**Claim:** The campaign greatly increased awareness.

**Evidence:** Surveyed awareness rose from 40% to 42%.

**Original expected label:** contradicting

**Reviewed label:** contradicting

**Review status:** provisional_retain

**Evidence rationale:** An increase from 40% to 42% does not ordinarily support 'greatly increased'.

**Review note:** An increase from 40% to 42% does not ordinarily support 'greatly increased'.

### H054 — magnitude

**Claim:** The campaign significantly increased awareness.

**Evidence:** Surveyed awareness rose from 40% to 65%.

**Original expected label:** supporting

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The increase from 40% to 65% is measurable, but the evidence does not establish statistical significance. This decision interprets 'significantly' in the statistical sense.

**Review note:** The increase from 40% to 65% is measurable, but the evidence does not establish statistical significance. This decision interprets 'significantly' in the statistical sense.

### H055 — relevant_not_supportive

**Claim:** The new park reduced neighborhood crime.

**Evidence:** The city spent $2 million building the new park.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Construction spending provides context but does not establish a reduction in neighborhood crime.

**Review note:** Construction spending provides context but does not establish a reduction in neighborhood crime.

### H056 — relevant_not_supportive

**Claim:** The new park reduced neighborhood crime.

**Evidence:** Residents reported that the park is attractive and well maintained.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Positive comments about appearance and maintenance do not establish crime outcomes.

**Review note:** Positive comments about appearance and maintenance do not establish crime outcomes.

### H057 — relevant_not_supportive

**Claim:** The school lunch program improved attendance.

**Evidence:** The school lunch program served 12,000 meals last month.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Meal counts measure program activity, not whether attendance improved.

**Review note:** Meal counts measure program activity, not whether attendance improved.

### H058 — relevant_not_supportive

**Claim:** The school lunch program improved attendance.

**Evidence:** Attendance increased from 88% to 93% after the lunch program began, with no other explanation provided.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Attendance rose after the program, but causation is not established.

**Review note:** Attendance rose after the program, but causation is not established.

### H059 — relevant_not_supportive

**Claim:** The new filter makes drinking water safer.

**Evidence:** The filter's packaging uses recyclable materials.

**Original expected label:** insufficient

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** Recyclable packaging does not establish drinking-water safety.

**Review note:** Recyclable packaging does not establish drinking-water safety.

### H060 — relevant_not_supportive

**Claim:** The new filter makes drinking water safer.

**Evidence:** Independent tests found that the filter removed 95% of the tested contaminant from water.

**Original expected label:** supporting

**Reviewed label:** insufficient

**Review status:** provisional_retain

**Evidence rationale:** The test establishes removal of 95% of one tested contaminant, not that the water is broadly safer across relevant contaminants.

**Review note:** The test establishes removal of 95% of one tested contaminant, not that the water is broadly safer across relevant contaminants.

## 6. Verification

- Candidate and review case IDs match.
- All 60 reviewed labels match the candidate labels.
- Original V1 holdout was not modified by this generator.
- This document is a record of the reviewed diagnostic dataset.

## 7. Limitations

- The candidate is derived from the original holdout cases.
- Revised labels do not make it an independent test set.
- Results must not be presented as final production accuracy.
- Human review remains necessary for ambiguous evidence.
