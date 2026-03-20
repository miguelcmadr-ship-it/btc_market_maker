import asyncio
import json
import websockets
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orderbook import OrderBook

KRAKEN_WS = "wss://ws.kraken.com/"

STALE_TIMEOUT = 5  # seconds before feed is considered disconnected

async def run_kraken(book):
    while True:  # outer reconnection loop
        try:
            # Connect and subscribe to Kraken book feed
            async with websockets.connect(KRAKEN_WS) as ws:
                last_update_ts = None

                subscribe_msg = {
                    "event": "subscribe",
                    "pair": ["XBT/USD"],
                    "subscription": {"name": "book", "depth": 10}
                }
                await ws.send(json.dumps(subscribe_msg))
                while True:
                    try:
                        # Use wait_for so we can periodically check staleness
                        # even if no message arrives
                        msg = await asyncio.wait_for(ws.recv(), timeout=STALE_TIMEOUT)
                    except asyncio.TimeoutError:
                        # No message within timeout window — feed is stale
                        run_kraken.system_healthy = False
                        continue

                    data = json.loads(msg)

                    # Ignore system messages (heartbeats, status, etc.)
                    if isinstance(data, dict):
                        continue

                    if not isinstance(data, list) or len(data) < 2:
                        continue

                    book_data = data[1]

                    bids = []
                    asks = []

                    # Snapshot
                    if "bs" in book_data or "as" in book_data:
                        bids = [(float(p), float(q)) for p, q, *_ in book_data.get("bs", [])]
                        asks = [(float(p), float(q)) for p, q, *_ in book_data.get("as", [])]

                    # Incremental updates
                    if "b" in book_data or "a" in book_data:
                        bids += [(float(p), float(q)) for p, q, *_ in book_data.get("b", [])]
                        asks += [(float(p), float(q)) for p, q, *_ in book_data.get("a", [])]

                    # Apply updates if any
                    if bids or asks:
                        last_update_ts = time.time()
                        run_kraken.system_healthy = True

                        for price, size in bids:
                            book.update_bid(price, size)

                        for price, size in asks:
                            book.update_ask(price, size)

                        book.mid_price()

        except Exception as e:
            run_kraken.system_healthy = False
            print(f"[kraken] Connection error: {e} — reconnecting in 3s")
            await asyncio.sleep(3)