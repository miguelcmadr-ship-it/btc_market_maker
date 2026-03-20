class Quoter:

    def __init__(self, base_spread=10.0, base_size=0.5, max_size=5):
        self.base_spread = base_spread
        self.base_size = base_size
        self.max_size = max_size


    def quote(self, fair_value, inventory=0,vol=0):

        if fair_value is None:
            return None

        inventory_max = 50
        skew = inventory / inventory_max

        if skew > 0:
            bid_spread = self.base_spread / 2 * (1+skew)*(min(2, 1+vol)) #when long inventory, widen bid spread i.e. lower bid price to buy less
            ask_spread = self.base_spread / 2 * (1-skew)*(min(2, 1+vol)) #when long inventory, narrow ask spread i.e. lower ask price to sell more
            bid_size = min(self.max_size, self.base_size *(1-skew))*(max(0, 1-vol)) #when long inventory, reduce bid size to buy less
            ask_size = min(self.max_size, self.base_size *(1+skew))*(max(0, 1-vol)) #when long inventory, increase ask size to sell more
        else:
            bid_spread = self.base_spread / 2 * (1-abs(skew))*(min(2, 1+vol)) #when short inventory, narrow bid spread i.e. raise bid price to buy more
            ask_spread = self.base_spread / 2 * (1+abs(skew))*(min(2, 1+vol)) #when short inventory, widen ask spread i.e. raise ask price to sell less
            bid_size = min(self.max_size, self.base_size *(1+abs(skew)))*(max(0, 1-vol)) #when short inventory, increase bid size to buy more
            ask_size = min(self.max_size, self.base_size *(1-abs(skew)))*(max(0, 1-vol)) #when short inventory, decrease ask size to sell less

        bid = fair_value - bid_spread
        ask = fair_value + ask_spread        

        return {
            "bid_price": round(bid, 2),
            "ask_price": round(ask, 2),
            "bid_size": round(bid_size, 4),
            "ask_size": round(ask_size, 4)
        }