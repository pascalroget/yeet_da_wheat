from dotenv import load_dotenv
import alpaca_trade_api as api
import asyncio
import pandas as pd
import sys
import os
from pytz import timezone

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Set credentials in .env file - rename .env-example and edit to fit
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
load_dotenv()

# How much of account to allocate (%, 0-1)
risk = 1
# Stop limit (%, 0-1)
stop = 0.95

# Asset to monitor (SPY by default)
spy = 'SPY'

# Asset used as volatility indicator (VXX by default)
volatility = 'VXX'

# ETF for up (leverage should ideally match spy_down)
spy_up = 'SPXL'
# ETF for down  (leverage should ideally match spy_up)
spy_down = 'SPXS'


# REST API Instance for placing orders
order_api = api.REST(
        base_url=os.getenv("ORDERS_BASE_URL"),
        key_id=os.getenv("ORDERS_KEY"),
        secret_key=os.getenv("ORDERS_SECRET")
        )

# Streaming API instance for real-time quotes
quote_api = api.StreamConn(
        base_url=os.getenv("QUOTES_BASE_URL"),
        key_id=os.getenv("QUOTES_KEY"),
        secret_key=os.getenv("QUOTES_SECRET")
)


def run(tickers, order_api, quote_api):

    # Use trade updates to keep track of our portfolio
    @conn.on(r'trade_update')
    async def handle_trade_update(conn, channel, data):
        print('Trade update')

    @conn.on(r'A$')
    async def handle_second_bar(conn, channel, data):
        print('1s bar update')


# Recursive function to prevent program from dying on failed/terminated websocket connection, which seems to happen
# several times a day in my testing
def run_ws(conn, channels):
    try:
        conn.run(channels)
    except Exception as e:
        print(e)
        conn.close()
        run_ws(conn, channels)


# Main program entry
if __name__ == "__main__":
