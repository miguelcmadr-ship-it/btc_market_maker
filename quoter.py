class Quoter:

    def __init__(self, base_spread=10.0, base_size=0.5, max_size=5):
        self.base_spread = base_spread
        self.base_size = base_size
        self.max_size = max_size


    def quote(self, fair_value, inventory=0,vol=0):

        if fair_value is None:
            return None

        inventory_max = 50
        skew = inventory / inventory_max # Normalize inventory to a range of -1 to 1, where -1 represents maximum short position and +1 represents maximum long position. This will allow us to adjust our quotes based on how far we are from a neutral inventory position.

        if skew > 0:
            bid_spread = self.base_spread / 2 * (1+skew)*(min(2, 1+vol)) #when long inventory, widen bid spread i.e. lower bid price to buy less // Widen spreads when volatility is high 
            ask_spread = self.base_spread / 2 * (1-skew)*(min(2, 1+vol)) #when long inventory, narrow ask spread i.e. lower ask price to sell more // Widen spreads when volatility is high
            bid_size = min(self.max_size, self.base_size *(1-skew))*(max(0, 1-vol)) #when long inventory, reduce bid size to buy less // Reduce size when volatility is high; do not trade when 500 ms-tick vol spikes past 1 
            ask_size = min(self.max_size, self.base_size *(1+skew))*(max(0, 1-vol)) #when long inventory, increase ask size to sell more // Reduce size when volatility is high; do not trade when 500 ms-tick vol spikes past 1
        else:
            bid_spread = self.base_spread / 2 * (1-abs(skew))*(min(2, 1+vol)) #when short inventory, narrow bid spread i.e. raise bid price to buy more // Widen spreads when volatility is high
            ask_spread = self.base_spread / 2 * (1+abs(skew))*(min(2, 1+vol)) #when short inventory, widen ask spread i.e. raise ask price to sell less // Widen spreads when volatility is high
            bid_size = min(self.max_size, self.base_size *(1+abs(skew)))*(max(0, 1-vol)) #when short inventory, increase bid size to buy more // Reduce size when volatility is high; do not trade when 500 ms-tick vol spikes past 1
            ask_size = min(self.max_size, self.base_size *(1-abs(skew)))*(max(0, 1-vol)) #when short inventory, decrease ask size to sell less // Reduce size when volatility is high; do not trade when 500 ms-tick vol spikes past 1

        bid = fair_value - bid_spread
        ask = fair_value + ask_spread        

        return {
            "bid_price": round(bid, 2),
            "ask_price": round(ask, 2),
            "bid_size": round(bid_size, 4),
            "ask_size": round(ask_size, 4)
        }