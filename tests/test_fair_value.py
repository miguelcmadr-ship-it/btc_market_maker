from fair_value import compute_fair_value


def test_fair_value_basic():
    mids = [100, 102]
    fv = compute_fair_value(mids)

    assert fv == 101


def test_fair_value_ignores_none():
    mids = [100, None, 102]
    fv = compute_fair_value(mids)

    assert fv == 101


def test_fair_value_all_none():
    mids = [None, None]

    assert compute_fair_value(mids) is None


def test_fair_value_empty():
    assert compute_fair_value([]) is None