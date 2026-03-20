def compute_fair_value(mid_prices):
    mids = [m for m in mid_prices if m is not None]

    if not mids:
        return None

    return sum(mids) / len(mids)