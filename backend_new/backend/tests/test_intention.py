import pytest
from backend.tools.intention import IntentionClassifier

clf = IntentionClassifier()

@pytest.mark.parametrize("q,expected", [
    ("hi there", "generic"),
    ("10 hard rock songs from the 80s between 3 and 5 minutes", "suggestion"),
    ("remove #2 and #4 and replace with faster tracks", "modification"),
])
def test_intention(q, expected):
    out = clf.classify(q)
    assert out.intention == expected
