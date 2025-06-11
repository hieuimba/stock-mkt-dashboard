import logging
import yfinance as yf
import pandas as pd
import azure.functions as func
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    # retrieve, format tickers list request body
    tickers = req.get_json().get("tickers")

    if tickers == []:
        return func.HttpResponse(json.dumps({}), status_code=200)

    tickers = [d["Ticker"] for d in tickers]

    logging.info(f"Tickers list received: {tickers}")

    index_df = get_ticker_data(tickers)
    logging.info(index_df)

    # calc returns & technical indicators
    index_df["Return"] = index_df.groupby("Ticker")["Close"].pct_change()
    index_df = calculate_technical_indicators(index_df)
    logging.info(index_df)

    # write to json
    index_df["Date"] = index_df["Date"].astype(str)
    response = index_df.to_json(orient="records")

    return func.HttpResponse(response, status_code=200)


def get_ticker_data(tickers):
    tickers = ["DX-Y.NYB" if x == "^DXY" else x for x in tickers]
    data = yf.download(tickers, interval="1d", period="1y").stack().reset_index()
    data = data.rename(columns={"level_1": "Ticker"})
    data["Ticker"] = data["Ticker"].replace("DX-Y.NYB", "^DXY")
    data = data.sort_values(by=["Ticker", "Date"])
    data["Date"] = data["Date"].dt.date

    return data[["Ticker", "Date", "Open", "High", "Low", "Close", "Volume"]]


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

# trigger upgrade of library
