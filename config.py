import streamlit as st
import json
import pandas as pd
import requests
import numpy as np

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

# stocks screen settings:
signals_sorted = ['52WkRange', 'KCPos', 'SigmaSpike','RVol']
yr_range_bins_sorted = ["> 100", "87.5 - 100", "75 - 87.5", "62.5 - 75", "50 - 62.5", "37.5 - 50", "25 - 37.5", "12.5 - 25", "0 - 12.5", "< 0"]
sigma_spike_bins_sorted = ["> 4", "3 - 4", "2 - 3", "1 - 2", "0 - 1", "-1 - 0", "-2 - -1", "-3 - -2", "-4 - -3", "< -4"]
rvol_bins_sorted = ["> 5", "4 - 5", "3 - 4", "2 - 3", "1 - 2", "0 - 1"]

# queries settings:
timestamp_query = "SELECT MAX([DATE]) AS Date FROM analytics.TodaySnapshot"
unique_tickers_query = "SELECT COUNT(DISTINCT ticker) AS Count FROM analytics.TodaySnapshot Where SecType = 'Stock'"
market_summary_query = "SELECT S.Ticker, S.SecType, S.SigmaSpike, T.ShortName FROM analytics.TodaySnapShot S \
    Left Join config.TickerShortNames T on T.Ticker=S.Ticker\
        WHERE S.SecType = 'ETF'"
index_prices_query = "select  P.Ticker, T.Name,[Date], [Open], [High], [Low], [Close], Volume \
    from raw.Prices P Left Join raw.Tickers T on P.Ticker = T.Ticker \
        where T.SecType = 'Index'\
            AND [Date] >= DATEADD(month, -2, GETDATE())"