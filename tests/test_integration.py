from orderbook import OrderBook
from fair_value import compute_fair_value
from quoter import Quoter


def test_end_to_end_flow():
    ob1 = OrderBook()
    ob2 = OrderBook()

    # simulate two exchanges
    ob1.update_bid(100, 1)
    ob1.update_ask(102, 1)

    ob2.update_bid(101, 1)
    ob2.update_ask(103, 1)

    mid1 = ob1.mid_price()
    mid2 = ob2.mid_price()

    fv = compute_fair_value([mid1, mid2])

    q = Quoter()
    quote = q.quote(fv, inventory=0, vol=0)

    assert fv == 101.5
    assert quote["bid_price"] < fv
    assert quote["ask_price"] > fv