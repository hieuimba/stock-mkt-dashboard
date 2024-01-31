import streamlit as st
import json
import pandas as pd
import requests
from typing import List
import re

from datetime import datetime, timedelta


# Function to get current datetime in UTC-6 timezone
def get_current_datetime():
    return (datetime.utcnow() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")


st.sidebar.write(f"Current Time: {get_current_datetime()} UTC-6")
# color settings:
green = "#22c55e"
red = "#ef4444"
blue = "#0ea5e9"
yellow = "#f59e0b"
white = "#fafafa"
darkgrey = "#171717"


# Function to query data
@st.cache_data(ttl=60 * 60 * 24, max_entries=20)
def query(query: str) -> pd.DataFrame:
    url = st.secrets["DB_URL"]
    request = {"query": query}
    response = json.loads(requests.post(url, json=request).content.decode("utf-8"))
    return pd.DataFrame(response)


# Function to convert string to array of floats
def string_to_array(row: str) -> List[float]:
    values_list = [float(value) for value in row.split(",")]
    return values_list


# Function to apply positive & negative color formatting
def format_positive_negative_cell_color(val: float) -> str:
    color = red if val < 0 else green
    return f"color: {color}"


# Function to add space between capital letters
def add_space(match: re.Match) -> str:
    return " " + match.group(0)


# page settings:
condensed_page_style = """
    <style>
        div.block-container {padding-top:2rem;padding-bottom:3rem}
    </style>
"""

# stocks histogram bins settings:
signals_sorted = ["52WkRange", "KCPos", "SigmaSpike", "RVol"]
yr_range_bins_sorted = [
    "> 100",
    "87.5 - 100",
    "75 - 87.5",
    "62.5 - 75",
    "50 - 62.5",
    "37.5 - 50",
    "25 - 37.5",
    "12.5 - 25",
    "0 - 12.5",
    "< 0",
]
sigma_spike_bins_sorted = [
    "> 4",
    "3 - 4",
    "2 - 3",
    "1 - 2",
    "0 - 1",
    "-1 - 0",
    "-2 - -1",
    "-3 - -2",
    "-4 - -3",
    "< -4",
]
rvol_bins_sorted = ["> 5", "4 - 5", "3 - 4", "2 - 3", "1 - 2", "0 - 1"]

# queries settings:
timestamp_query = "SELECT MAX([DATE]) AS Date FROM analytics.TodaySnapshot"
unique_tickers_query = "SELECT COUNT(DISTINCT ticker) AS Count FROM analytics.TodaySnapshot Where SecType = 'Stock'"

stock_his_query = "SELECT * from visual.StockHistogram"
stock_ranking_query = "SELECT * from visual.StockRanking"

index_prices_query = "select * from visual.CandlestickChart where SecType = 'Index'"
index_table_query = "select * from visual.PerformanceTable where SecType = 'Index'"

one_day_return_query = "SELECT S.Ticker, S.SecType, S.SigmaSpike, T.ShortName FROM analytics.TodaySnapShot S \
    Left Join config.TickerShortNames T on T.Ticker=S.Ticker\
        WHERE S.SecType = 'ETF'"

sector_prices_query = "select * from visual.CandlestickChart where SecType = 'ETF'"
sector_table_query = "select * from visual.PerformanceTable where SecType = 'ETF'"

sector_return_query = "select T.ShortName as 'Name', [Date], [Return], [Order] from raw.Prices P\
    left join config.TickerShortNames T on T.Ticker = P.Ticker\
        where T.SecType = 'ETF' AND P.Ticker LIKE 'XL%' AND [RETURN] is not null"

stock_heatmap_query = "select * from visual.StockHeatmap"
