
import pytest

from src.verity.evidence import has_population_mismatch

from src.verity.evidence import classify_evidence


@pytest.mark.parametrize(
    ("claim", "evidence", "expected"),
    [
        (
            "The policy increases employment.",
            "The policy failed to increase employment.",
            "contradicting",
        ),
        (
            "The supplement improves sleep quality.",
            "The supplement may not improve sleep quality.",
            "insufficient",
        ),
        (
            "The device reduces energy consumption.",
            "The device does not reduce energy consumption in the tested conditions.",
            "insufficient",
        ),
        (
            "The exercise plan improves cardiovascular fitness.",
            "Participants using the exercise plan showed no improvement in cardiovascular fitness compared with the control group.",
            "contradicting",
        ),
        (
            "The service is available every day.",
            "The service is available only on weekdays.",
            "contradicting",
        ),
        (
            "The scheme increases rural employment.",
            "The scheme increased urban employment.",
            "insufficient",
        ),
        (
            "The medicine improves overall health.",
            "The medicine improves sleep quality, but other health outcomes were not measured.",
            "insufficient",
        ),
        (
            "The program improves employee productivity.",
            "The program improved productivity in one department but reduced it in another.",
            "insufficient",
        ),
        (
            "The treatment reduces pain.",
            "The treatment may reduce pain in some patients.",
            "insufficient",
        ),
        (
            "The program improves school attendance.",
            "Attendance increased from 88% to 93% after the program, but no control group was used.",
            "insufficient",
        ),
        (
            "The new policy improves public transport reliability.",
            "The new policy improved public transport reliability, but the evaluation covered only one city.",
            "insufficient",
        ),
                (
            "The treatment is effective for patients with moderate disease.",
            "The treatment is effective for patients with mild disease.",
            "insufficient",
        ),
    ],
)
def test_classifier_improvement_cases(claim, evidence, expected):
    assert classify_evidence(claim, evidence) == expected

def test_detects_disease_severity_mismatch():
    claim = "The therapy reduces symptoms in patients with moderate disease."
    evidence = "The therapy reduced symptoms in patients with mild disease."

    assert has_population_mismatch(claim, evidence) is True