import streamlit as st
import json
import pandas as pd
import requests
import numpy as np


# color settings:
green = "#22c55e"
red = "#ef4444"
blue = "#0ea5e9"

# Function to query data
@st.cache_data(ttl = 3600)
def query(query):
    url =  st.secrets["DB_URL"]
    request = {"query": query}
    response = json.loads(requests.post(url, json=request).content.decode('utf-8'))
    return pd.DataFrame(response)

# Function to convert string to array of floats
def string_to_array(row):
    values_list = [float(value) for value in row.split(",")]
    return np.array(values_list)


# Function to apply positive & negative color formatting
def format_positive_negative_cell_color(val):
    color = red if val < 0 else green
    return f'color: {color}'

# stocks screen settings:
signals_sorted = ['52WkRange', 'KCPos', 'SigmaSpike','RVol']
yr_range_bins_sorted = ["> 100", "87.5 - 100", "75 - 87.5", "62.5 - 75", "50 - 62.5", "37.5 - 50", "25 - 37.5", "12.5 - 25", "0 - 12.5", "< 0"]
sigma_spike_bins_sorted = ["> 4", "3 - 4", "2 - 3", "1 - 2", "0 - 1", "-1 - 0", "-2 - -1", "-3 - -2", "-4 - -3", "< -4"]
rvol_bins_sorted = ["> 5", "4 - 5", "3 - 4", "2 - 3", "1 - 2", "0 - 1"]

# queries settings:
timestamp_query = "SELECT MAX([DATE]) AS Date FROM analytics.TodaySnapshot"
unique_tickers_query = "SELECT COUNT(DISTINCT ticker) AS Count FROM analytics.TodaySnapshot Where SecType = 'Stock'"
one_day_return_query = "SELECT S.Ticker, S.SecType, S.SigmaSpike, T.ShortName FROM analytics.TodaySnapShot S \
    Left Join config.TickerShortNames T on T.Ticker=S.Ticker\
        WHERE S.SecType = 'ETF'"
index_prices_query = "select  P.Ticker, T.Name,[Date], [Open], [High], [Low], [Close], Volume \
    from raw.Prices P Left Join raw.Tickers T on P.Ticker = T.Ticker \
        where T.SecType = 'Index'\
            AND [Date] >= DATEADD(month, -2, GETDATE())"
index_table_query = "select T.Name, S.Ticker, S.[Return] as 'OneDayReturn', R.OneWeekReturn as 'OneWeekReturn',\
      R.OneMonthReturn as 'OneMonthReturn', R.OneQuarterReturn as 'OneQuarterReturn'\
        , R.OneYearReturn as 'OneYearReturn', S.SigmaSpike, S.KCPos/100 as 'MonthRange', S.[C%52WkRange]/100 as 'YearRange'\
    from analytics.TodaySnapshot S\
    left join raw.Tickers T on T.Ticker = S.Ticker \
    left join analytics.AggReturns R on R.Ticker  = S.Ticker\
        where S.SecType = 'Index'"

etf_prices_query = "select  P.Ticker, T.ShortName as 'Name',[Date], [Open], [High], [Low], [Close], Volume \
    from raw.Prices P Left Join config.TickerShortNames T on P.Ticker = T.Ticker \
        where T.SecType = 'ETF'\
            AND [Date] >= DATEADD(month, -2, GETDATE())\
			AND P.Ticker LIKE 'XL%'"

# formatting settings
index_table_rename_source = ['OneDayReturn', 'OneWeekReturn','OneMonthReturn','OneQuarterReturn','OneYearReturn', 'SigmaSpike','MonthRange','YearRange']
index_table_rename_target = ['One Day Return', 'One Week Return','One Month Return','One Quarter Return','One Year Return', 'Sigma Spike','Month Range','Year Range']

index_table_percentage_format_subset = ['One Day Return', 'One Week Return','One Month Return','One Quarter Return','One Year Return', 'Sigma Spike','Month Range','Year Range']
index_table_color_format_subset = ['One Day Return', 'One Week Return','One Month Return','One Quarter Return','One Year Return', 'Sigma Spike']

