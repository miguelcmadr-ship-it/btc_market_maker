import asyncio
import json
import websockets
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orderbook import OrderBook

BINANCE_WS = "wss://stream.binance.com:9443/ws/btcusdt@depth"

async def run_binance(book):
    while True:  # outer reconnection loop
        try:
            async with websockets.connect(BINANCE_WS) as ws:
                last_update_id = None

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    # Binance sequence fields
                    first_update_id = data.get("U")
                    final_update_id = data.get("u")

                    # Safety check
                    if first_update_id is None or final_update_id is None:
                        continue

                    # Initialize sequence tracking
                    if last_update_id is None:
                        last_update_id = final_update_id
                        run_binance.system_healthy = True

                    # Drop stale updates
                    elif final_update_id <= last_update_id:
                        continue

                    # Detect gaps — reset and mark unhealthy until re-sync
                    elif first_update_id > last_update_id + 1:
                        run_binance.system_healthy = False
                        last_update_id = None
                        continue

                    else:
                        last_update_id = final_update_id
                        run_binance.system_healthy = True

                    for bid in data["b"]:
                        price = float(bid[0])
                        size = float(bid[1])
                        book.update_bid(price, size)

                    for ask in data["a"]:
                        price = float(ask[0])
                        size = float(ask[1])
                        book.update_ask(price, size)

                    book.mid_price()

        except Exception as e:
            run_binance.system_healthy = False
            print(f"[binance] Connection error: {e} — reconnecting in 3s")
            await asyncio.sleep(3)