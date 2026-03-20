from collections import deque
import time
import numpy as np

class OrderBook:
    # Simple in-memory order book implementation
    def __init__(self, window=100):
        self.bids = {}
        self.asks = {}
        self.prices = deque(maxlen=window)
        self.data = {
            "mid_price": None,
            "volatility": None
        }
        self.last_update_ts = None
        self.is_stale = False

    # Update bid or ask with new price and size
    def update_bid(self, price, size):
        if size == 0:
            self.bids.pop(price, None) # Remove bid if size is zero
        else:
            self.bids[price] = (size, time.time())  # store timestamp alongside size

        self.last_update_ts = time.time()
        self.is_stale = False # Mark book as fresh after update

    def update_ask(self, price, size):
        if size == 0:
            self.asks.pop(price, None) # Remove ask if size is zero
        else:
            self.asks[price] = (size, time.time())  # store timestamp alongside size
        self.last_update_ts = time.time()
        self.is_stale = False # Mark book as fresh after update

        self.last_update_ts = time.time()
        self.is_stale = False # Mark book as fresh after update

    def purge_stale(self, timeout=5):          
        now = time.time()
        self.bids = {
            p: (s, ts) for p, (s, ts) in self.bids.items()  
            if now - ts <= timeout
        }
        self.asks = {
            p: (s, ts) for p, (s, ts) in self.asks.items()
            if now - ts <= timeout
        }

    def best_bid(self):
        if not self.bids:
            return None
        price = max(self.bids.keys())
        size, _ = self.bids[price]  
        return price, size

    def best_ask(self):
        if not self.asks:
            return None
        price = min(self.asks.keys())
        size, _ = self.asks[price] 
        return price, size

    def mid_price(self):
        bid = self.best_bid()
        ask = self.best_ask()
        if not bid or not ask:
            return None

        mid = (bid[0] + ask[0]) / 2
        self.data["mid_price"] = mid
        self.prices.append(mid)

        return mid
    
    def compute_volatility(self):
        if len(self.prices) < 2:
            return None

        returns = np.diff(np.log(self.prices))
        vol = float(np.std(returns))

        self.data["volatility"] = vol
        return vol
