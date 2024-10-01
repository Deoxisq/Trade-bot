from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.enums import OrderSide, QueryOrderStatus, TimeInForce
from alpaca.data.live import StockDataStream
from alpaca.data import StockHistoricalDataClient, StockTradesRequest
from datetime import datetime, timedelta, time
from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd
import alpaca_trade_api as tradeapi
import requests
import json
import os
import time
import matplotlib



stocklist = ('AAPL',"NVDA",'MSFT' ,'AMZN' ,'META' ,'GOOGL' , "sBRK.B" ,'GOOG' , 'LLY' , 'AVGO')
holding = []

while True:
    #ALPACA API KEYS
    BASE_URL = 'https://paper-api.alpaca.markets/v2'
    KEY_ID = 'PKKN687PI6C8D094ROH6'
    SECRET_KEY = 'ayFOvbIG47N72VeKHaTrBsqnRRawFWULfbcgwtzd'

    #Specifying accounts for data and trading
    history_account = StockHistoricalDataClient(KEY_ID, SECRET_KEY)
    account = TradingClient(KEY_ID, SECRET_KEY, paper=True)

    #asking which stock you want to run the algo on
    stock_symbol = "BTC/USD"

    trade_data = StockTradesRequest(
        symbol_or_symbols = stock_symbol,
        timeframe = TimeFrame.Day,
        start = datetime.now()-timedelta(minutes = 1),
        end = datetime.now(),
        extended_hours = True,
        limit = 100
    )
    past_minute_trades = (str(history_account.get_stock_trades(trade_data)))

    #data sets for limit buys and normal buys
    order_data = MarketOrderRequest(
        symbol = stock_symbol,
        qty = 1,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.GTC,
        limit = 1000   #marketdata limit
    )

    limit_order_data = LimitOrderRequest(
        symbol = stock_symbol,
        qty = 1,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.DAY,
        limit_price = 300.00 #this is just a random number
    )

    sell_data = MarketOrderRequest(
        symbol = stock_symbol,
        qty = 1,
        side = OrderSide.SELL,
        time_in_force = TimeInForce.GTC
    )

    # buy function for placing market orders
    def buy():
        order = account.submit_order(order_data)
        print(order)

    # buy function for placing limit orders
    def limitbuy():
        limitorder = account.submit_order(limit_order_data)

    #sell function

    def sell():
        order = account.submit_order(sell_data)
        print(order)

    openai_api_key = "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"

    if openai_api_key is None:
        raise ValueError("OpenAI API key is not set in environment variables.")

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": f"Should I buy or sell {stock_symbol} based on the trades presented here: {past_minute_trades}? please analyze the market data and give a definitive one-word answer that's either Buy. or Sell."
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        print("Response from OpenAI:", response.json())
        print('\n')
        print(response.json()['choices'][0]['message']['content'])
    else:
        print("Error:", response.status_code, response.text)

    #Automate the trades based on the response from the API
    if (response.json()['choices'][0]['message']['content']) == "Buy.":
        buy()
        holding.append(stock_symbol)
    elif (response.json()['choices'][0]['message']['content']) == "Sell." and (stock_symbol) in holding:
        sell()
        holding
    else:
        print("No trade made. Lock the fuck in.")

    time.sleep(15)