import logging
from finvizfinance.screener.overview import Overview
import json

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    exchange = req.route_params.get("exchange")

    stock_overview = Overview()

    stock_filters_dict = {"Market Cap.": "+Small (over $300mln)", "Exchange": exchange}
    stock_overview.set_filter(filters_dict=stock_filters_dict)
    stock_df = stock_overview.screener_view()
    stock_df = format_df(stock_df, exchange, "Stock")

    response = stock_df.to_json(orient="records")

    return func.HttpResponse(response, status_code=200)


def format_df(df, exchange, sec_type):
    df = df.sort_values("Market Cap")
    df = df.rename(
        columns={"Ticker\n\n": "Ticker", "Company": "Name", "Market Cap": "MarketCap"}
    )
    df["SecType"] = sec_type
    df["Exchange"] = exchange
    df = df[
        [
            "Ticker",
            "Name",
            "SecType",
            "Exchange",
            "Sector",
            "Industry",
            "Country",
            "MarketCap",
        ]
    ]

    # replace - with .
    df["Ticker"] = df["Ticker"].str.replace("-", ".")

    return df
