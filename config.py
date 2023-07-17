import streamlit as st
import json
import pandas as pd
import requests


# color settings:
green = "#22c55e"
red = "#ef4444"
blue = "#0ea5e9"
yellow = "#f59e0b"
white = "#fafafa"
darkgrey = "#171717"

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
    return values_list


# Function to apply positive & negative color formatting
def format_positive_negative_cell_color(val):
    color = red if val < 0 else green
    return f'color: {color}'

# page settings:
condensed_page_style = """
    <style>
        div.block-container {padding-top:2rem;padding-bottom:3rem}
    </style>
"""

# stocks histogram bins settings:
signals_sorted = ['52WkRange', 'KCPos', 'SigmaSpike','RVol']
yr_range_bins_sorted = ["> 100", "87.5 - 100", "75 - 87.5", "62.5 - 75", "50 - 62.5", "37.5 - 50", "25 - 37.5", "12.5 - 25", "0 - 12.5", "< 0"]
sigma_spike_bins_sorted = ["> 4", "3 - 4", "2 - 3", "1 - 2", "0 - 1", "-1 - 0", "-2 - -1", "-3 - -2", "-4 - -3", "< -4"]
rvol_bins_sorted = ["> 5", "4 - 5", "3 - 4", "2 - 3", "1 - 2", "0 - 1"]

# queries settings:
timestamp_query = "SELECT MAX([DATE]) AS Date FROM analytics.TodaySnapshot"
unique_tickers_query = "SELECT COUNT(DISTINCT ticker) AS Count FROM analytics.TodaySnapshot Where SecType = 'Stock'"

index_prices_query = "select  P.Ticker, T.Name,[Date], [Open], [High], [Low], [Close],[Return], Volume \
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
one_day_return_query = "SELECT S.Ticker, S.SecType, S.SigmaSpike, T.ShortName FROM analytics.TodaySnapShot S \
    Left Join config.TickerShortNames T on T.Ticker=S.Ticker\
        WHERE S.SecType = 'ETF'"

etf_prices_query = "select  P.Ticker, T.ShortName as 'Name',[Date], [Open], [High], [Low], [Close],[Return], Volume \
    from raw.Prices P Left Join config.TickerShortNames T on P.Ticker = T.Ticker \
        where T.SecType = 'ETF'\
            AND [Date] >= DATEADD(month, -2, GETDATE())\
			AND P.Ticker LIKE 'XL%'\
                ORDER BY Ticker, Date"
etf_table_query = "select T.Name, S.Ticker, S.[Return] as 'OneDayReturn', R.OneWeekReturn as 'OneWeekReturn',\
      R.OneMonthReturn as 'OneMonthReturn', R.OneQuarterReturn as 'OneQuarterReturn'\
        , R.OneYearReturn as 'OneYearReturn', S.SigmaSpike, S.KCPos/100 as 'MonthRange', S.[C%52WkRange]/100 as 'YearRange'\
    from analytics.TodaySnapshot S\
    left join raw.Tickers T on T.Ticker = S.Ticker \
    left join analytics.AggReturns R on R.Ticker  = S.Ticker\
        where S.SecType = 'ETF' AND S.Ticker LIKE 'XL%'\
            Order by S.Ticker"
etf_return_query_one_month_query = "select T.ShortName as 'Name', [Date], [Return], [Order] from raw.Prices P\
    left join config.TickerShortNames T on T.Ticker = P.Ticker\
        where T.SecType = 'ETF' AND P.Ticker LIKE 'XL%' AND [RETURN] is not null AND [Order] <=20"
etf_return_query_one_year_query = "select T.ShortName as 'Name', [Date], [Return], [Order] from raw.Prices P\
    left join config.TickerShortNames T on T.Ticker = P.Ticker\
        where T.SecType = 'ETF' AND P.Ticker LIKE 'XL%' AND [RETURN] is not null"

stock_heatmap_query = "select TOP 1000 S.Ticker,S.SecType,S.[Return], COALESCE(S.SigmaSpike, 0) as SigmaSpike, T.Sector, T.Industry, T.MarketCap\
    from analytics.TodaySnapshot S\
    left join raw.Tickers T on T.Ticker = S.Ticker \
    where S.SecType = 'Stock'\
    order by MarketCap desc"

# summary table settings
sum_table_rename_source = ['OneDayReturn', 'OneWeekReturn','OneMonthReturn','OneQuarterReturn','OneYearReturn', 'SigmaSpike','MonthRange','YearRange']
sum_table_rename_target = ['One Day Return', 'One Week Return','One Month Return','One Quarter Return','One Year Return', 'Sigma Spike','Month Range','Year Range']

sum_table_percentage_format_subset = ['One Day Return', 'One Week Return','One Month Return','One Quarter Return','One Year Return', 'Sigma Spike','Month Range','Year Range']
sum_table_color_format_subset = ['One Day Return', 'One Week Return','One Month Return','One Quarter Return','One Year Return', 'Sigma Spike']


