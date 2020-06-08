from dotenv import load_dotenv
import alpaca_trade_api as api
import asyncio
import pandas as pd
import sys
import os
from pytz import timezone
from datetime import datetime, timedelta
import art


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
    @quote_api.on(r'trade_update')
    async def handle_trade_update(conn, channel, data):
        print('Trade update')

    @quote_api.on(r'A$')
    async def handle_second_bar(conn, channel, data):
        print('1s bar update')

    # Enter main loop
    run_ws(conn, channels)


# Main loop
# Recursive function to prevent program from dying on failed/terminated websocket connection, which seems to happen
# several times a day in my testing
def run_ws(conn, channels):
    try:
        conn.run(channels)
    except Exception as e:
        print(e)
        # Sometimes the connection is left open, we attempt to close for safety
        conn.close()
        run_ws(conn, channels)


def ascii_logo():
    return art.text2art('YeetDaWheat')

# Main program entry
if __name__ == "__main__":

    print(ascii_logo())

    # Get when the market opens or opened today
    nyc = timezone('America/New_York')
    today = datetime.today().astimezone(nyc)
    today_str = datetime.today().astimezone(nyc).strftime('%Y-%m-%d')
    calendar = order_api.get_calendar(start=today_str, end=today_str)[0]

    market_open_date = calendar.date.strftime('%Y-%m-%d').split()[0]

    # Quit if market is closed
    if (market_open_date != today_str):
        print('Market is closed today. Algorithm should be started on market days prior to open, and stopped after close.')
        print(f'Next market open: {market_open_date}')
        exit(1)


    market_open = today.replace(
        hour=calendar.open.hour,
        minute=calendar.open.minute,
        second=0
    )
    market_open = market_open.astimezone(nyc)
    market_close = today.replace(
        hour=calendar.close.hour,
        minute=calendar.close.minute,
        second=0
    )
    market_close = market_close.astimezone(nyc)
    print(f'Today is {today_str}\nMarket next opens {calendar.date}')


