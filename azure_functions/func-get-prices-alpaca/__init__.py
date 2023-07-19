import logging
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta
import json
import pandas as pd
import azure.functions as func
import os

pd.set_option("display.max_columns", None)

current_date = datetime.now().date()
last_year_date = current_date - timedelta(days=365)
last_year_date_string = last_year_date.strftime("%Y-%m-%d")

api = REST(
    key_id=os.getenv("AlpacaKeyID"),
    secret_key=os.getenv("AlpacaSecretKey"),
    base_url="https://paper-api.alpaca.markets",
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    # retrieve, format tickers list
    tickers = req.get_json().get("tickers")

    if tickers == []:
        return func.HttpResponse(json.dumps({}), status_code=200)

    tickers = [d["Ticker"] for d in tickers]

    logging.info(f"Tickers list received: {tickers}")

    # get prices for all tickers in tickers list
    stocks = api.get_bars(
        tickers, timeframe=TimeFrame.Day, start=last_year_date_string, adjustment="all"
    ).df

    # format df
    stocks = stocks.reset_index()
    stocks = stocks.rename(columns={"timestamp": "date", "symbol": "ticker"})
    stocks = stocks[["ticker", "date", "open", "high", "low", "close", "volume"]]
    stocks["date"] = stocks["date"].dt.date
    stocks = stocks.rename(columns=lambda x: x.capitalize())

    # remove stocks without recent trading date
    last_trading_date = get_last_trading_date(current_date)
    stocks_filtered = stocks.groupby("Ticker").filter(
        lambda x: last_trading_date in x["Date"].values
    )
    logging.info(stocks_filtered)

    # calc returns & technical indicators
    stocks_filtered["Return"] = stocks_filtered.groupby("Ticker")["Close"].pct_change()
    stocks_filtered = calculate_technical_indicators(stocks_filtered)

    # write to json
    stocks_filtered["Date"] = stocks_filtered["Date"].astype(str)
    response = stocks_filtered.to_json(orient="records")

    logging.info(stocks_filtered)
    return func.HttpResponse(response, status_code=200)


def get_last_trading_date(date):
    response = api.get_calendar(start=date, end=date + timedelta(10))
    while date != response[0].date.to_pydatetime().date():
        date = date - timedelta(1)
        response = api.get_calendar(start=date, end=date + timedelta(10))
    return date


def calculate_technical_indicators(df):
    # Iterate over unique tickers
    tickers = df["Ticker"].unique()
    for ticker in tickers:
        # Filter data for the current ticker
        ticker_data = df[df["Ticker"] == ticker]

        # Calculate True Range (TR) for the current ticker
        tr = pd.concat(
            [
                ticker_data["High"] - ticker_data["Low"],
                abs(ticker_data["High"] - ticker_data["Close"].shift(1)),
                abs(ticker_data["Low"] - ticker_data["Close"].shift(1)),
            ],
            axis=1,
        ).max(axis=1)

        # Calculate Average True Range (ATR) for the current ticker
        atr = pd.Series(index=ticker_data.index, dtype=float)
        atr.iloc[0] = tr.iloc[0]  # Set the first ATR value as the first TR value

        for i in range(1, len(ticker_data)):
            atr.iloc[i] = ((atr.iloc[i - 1] * 20) + tr.iloc[i]) / 21

        # Calculate 21-day Exponential Moving Average (EMA) for the current ticker's close price
        ema_close = pd.Series(index=ticker_data.index, dtype=float)
        ema_close.iloc[0] = ticker_data["Close"].iloc[
            0
        ]  # Set the first EMA value as the first Close value

        for i in range(1, len(ticker_data)):
            ema_close.iloc[i] = (ticker_data["Close"].iloc[i] * 2 / (21 + 1)) + (
                ema_close.iloc[i - 1] * (1 - 2 / (21 + 1))
            )

        # Calculate 21-day Exponential Moving Average (EMA) for the current ticker's volume
        ema_volume = pd.Series(index=ticker_data.index, dtype=float)
        ema_volume.iloc[0] = ticker_data["Volume"].iloc[
            0
        ]  # Set the first EMA value as the first Volume value

        for i in range(1, len(ticker_data)):
            ema_volume.iloc[i] = (ticker_data["Volume"].iloc[i] * 2 / (21 + 1)) + (
                ema_volume.iloc[i - 1] * (1 - 2 / (21 + 1))
            )

        # Calculate Relative Volume (RVol) for the current ticker
        rvol = ticker_data["Volume"] / ema_volume.shift(1)

        # Calculate ATRSpike, KCUpper, and KCLower for the current ticker
        atr_spike = tr / atr.shift(1)
        kc_upper = ema_close + 2.5 * atr
        kc_lower = ema_close - 2.5 * atr

        # Calculate StdDev and SigmaSpike for the current ticker
        std_dev = (
            ticker_data.groupby("Ticker")["Return"]
            .rolling(21)
            .std()
            .reset_index(level=0, drop=True)
        )
        sigma_spike = ticker_data["Return"] / std_dev.shift(1)

        # Calculate the highest high and lowest low for the current ticker
        highest_high = ticker_data["High"].iloc[:-1].max()  # Exclude the last row
        lowest_low = ticker_data["Low"].iloc[:-1].min()  # Exclude the last row

        # Calculate the Order column as a reversed index
        order = range(len(ticker_data) - 1, -1, -1)

        # Update the TR, ATR, EMA, ATRSpike, KCUpper, KCLower, StdDev, SigmaSpike, HighestHigh, LowestLow, RVol, and ConsecutiveClose columns for the current ticker
        df.loc[df["Ticker"] == ticker, "StdDev"] = std_dev
        df.loc[df["Ticker"] == ticker, "SigmaSpike"] = sigma_spike
        df.loc[df["Ticker"] == ticker, "TR"] = tr
        df.loc[df["Ticker"] == ticker, "ATR"] = atr
        df.loc[df["Ticker"] == ticker, "ATRSpike"] = atr_spike
        df.loc[df["Ticker"] == ticker, "EMA"] = ema_close
        df.loc[df["Ticker"] == ticker, "KCUpper"] = kc_upper
        df.loc[df["Ticker"] == ticker, "KCLower"] = kc_lower
        df.loc[df["Ticker"] == ticker, "52WkHigh"] = highest_high
        df.loc[df["Ticker"] == ticker, "52WkLow"] = lowest_low
        df.loc[df["Ticker"] == ticker, "EMAVol"] = ema_volume
        df.loc[df["Ticker"] == ticker, "RVol"] = rvol
        df.loc[df["Ticker"] == ticker, "Order"] = order
    return df
