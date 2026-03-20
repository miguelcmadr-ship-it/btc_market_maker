import asyncio
from random import random
import time

from orderbook import OrderBook
from fair_value import compute_fair_value
from quoter import Quoter

from feeds.binance_feed import run_binance
from feeds.kraken_feed import run_kraken

binance_book = OrderBook()
kraken_book = OrderBook()

quoter = Quoter()


async def monitor():
    start_time = time.time() 

    inventory = 0

    while True:   
        binance_book.purge_stale()  # evict stale Binance levels
        kraken_book.purge_stale()   # evict stale Kraken levels
        binance_mid = binance_book.mid_price()
        kraken_mid = kraken_book.mid_price()
        
        fair = compute_fair_value([
            binance_mid,
            kraken_mid
        ])

        binance_bid = binance_book.best_bid()
        binance_ask = binance_book.best_ask()
        kraken_bid = kraken_book.best_bid()
        kraken_ask = kraken_book.best_ask()

        #If connectivity to an exchange is lost, we want to pause trading but keep monitoring the other feed. 
        binance_okay = all([binance_bid, binance_ask])
        kraken_okay = all([kraken_bid, kraken_ask])

        if not binance_okay and not kraken_okay:
            if time.time() - start_time > 2:  # only print after book is ready for a few seconds
                print("quote: None")
                print("status: PAUSED — both feeds disconnected")
            await asyncio.sleep(0.5)
            continue

        # skip loop if any book is not ready
        if not all([binance_bid, binance_ask, kraken_bid, kraken_ask]):
            await asyncio.sleep(0.1)
            continue

        # Determine best bid/ask across both exchanges for quoting 
        best_bid = max(binance_bid, kraken_bid, key=lambda x: x[0])
        best_ask = min(binance_ask, kraken_ask, key=lambda x: x[0])
        volatility = max(binance_book.compute_volatility(), kraken_book.compute_volatility())

        last_bid_trade = None # track last traded price on bid side to avoid repeat fills in this simple example
        last_ask_trade = None # track last traded price on ask side to avoid repeat fills in this simple example

        # SELL
        if fair < best_bid[0] and best_bid[0] != last_bid_trade:
            inventory -= min(1, quoter.quote(fair, inventory,volatility)["bid_size"], best_bid[1])
            last_bid_trade = best_bid[0]

        # BUY
        if fair > best_ask[0] and best_ask[0] != last_ask_trade:
            inventory += min(1, quoter.quote(fair, inventory,volatility)["ask_size"], best_ask[1])
            last_ask_trade = best_ask[0]

        quote = quoter.quote(fair, inventory, volatility)

        timestamp = time.time()

        print("------")

        print("timestamp:", timestamp)

        print("binance:", binance_book.best_bid(), binance_book.best_ask())

        print("kraken:", kraken_book.best_bid(), kraken_book.best_ask())

        print("fair_value:", fair)

        print("quote:", quote)
        # send bid/ask to exchange
        print("status: ACTIVE")

        await asyncio.sleep(0.5)


async def main():

    await asyncio.gather(
        run_binance(binance_book),
        run_kraken(kraken_book),
        monitor()
    )


if __name__ == "__main__":
    asyncio.run(main())