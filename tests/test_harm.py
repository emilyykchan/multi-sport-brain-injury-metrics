from brain_injury_metrics.harm import harm


def test_harm_published_weights():
    assert harm(100.0, 0.5) == 0.0148 * 100.0 + 15.6 * 0.5
