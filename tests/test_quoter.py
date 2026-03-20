from quoter import Quoter


def test_basic_quote_symmetry():
    q = Quoter(base_spread=10)

    result = q.quote(fair_value=100, inventory=0, vol=0)

    assert result["bid_price"] < 100
    assert result["ask_price"] > 100
    assert result["bid_price"] < result["ask_price"]


def test_quote_none_fair_value():
    q = Quoter()

    assert q.quote(None) is None


def test_inventory_skew_long():
    q = Quoter(base_spread=10)

    result = q.quote(fair_value=100, inventory=25, vol=0)

    # long → lower bid, more aggressive ask
    assert result["bid_price"] < 95  
    assert result["ask_price"] <= 105


def test_inventory_skew_short():
    q = Quoter(base_spread=10)

    result = q.quote(fair_value=100, inventory=-25, vol=0)

    # short → more aggressive bid
    assert result["bid_price"] >= 95
    assert result["ask_price"] > 105


def test_volatility_effect():
    q = Quoter(base_spread=10)

    low_vol = q.quote(100, inventory=0, vol=0)
    high_vol = q.quote(100, inventory=0, vol=2)

    # higher vol → wider spread
    low_spread = low_vol["ask_price"] - low_vol["bid_price"]
    high_spread = high_vol["ask_price"] - high_vol["bid_price"]

    assert high_spread > low_spread


def test_size_capped():
    q = Quoter(base_size=10, max_size=5)

    result = q.quote(100, inventory=0, vol=0)

    assert result["bid_size"] <= 5
    assert result["ask_size"] <= 5


