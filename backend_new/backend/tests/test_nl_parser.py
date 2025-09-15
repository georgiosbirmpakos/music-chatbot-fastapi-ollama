from backend.helpers.nl import nl_to_query_and_limit

def test_limit_and_durations():
    q, lim = nl_to_query_and_limit("10 hard rock songs from the 80s between 3 and 5 minutes")
    assert lim == 10
    assert q.genre and "hard" in q.genre.lower()
    assert q.decade == 1980
    assert q.min_duration_ms == 180000
    assert q.max_duration_ms == 300000
from backend.helpers.nl import nl_to_query_and_limit

def test_limit_and_durations():
    q, lim = nl_to_query_and_limit("10 hard rock songs from the 80s between 3 and 5 minutes")
    assert lim == 10
    assert q.genre and "hard" in q.genre.lower()
    assert q.decade == 1980
    assert q.min_duration_ms == 180000
    assert q.max_duration_ms == 300000
