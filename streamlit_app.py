import streamlit as st
import requests
import json 
import pandas as pd
import plotly.express as px
import numpy as np
st.set_page_config(layout="wide")

# Define the URL and payload for the POST request
url =  st.secrets["DB_URL"]

@st.cache_data(ttl = 3600)
def query(query):
    request = {"query": query}
    response = json.loads(requests.post(url, json=request).content.decode('utf-8'))
    return pd.DataFrame(response)

# Function to convert string to array of floats
def string_to_array(row):
    values_list = [float(value) for value in row.split(",")]
    return np.array(values_list)

# @st.cache_data(ttl = 3600)
# def query_prices(tickers_list):
#     tickers_string = ','.join(tickers_list)
#     query = f"EXEC GetClosePrices @Tickers = '{tickers_string}'"
#     request = {"query": query}
#     response = json.loads(requests.post(url, json=request).content.decode('utf-8'))
#     ticker_dict = {}
#     for entry in response:
#         ticker = entry['Ticker']
#         close_price = entry['close']
        
#         if ticker not in ticker_dict:
#             ticker_dict[ticker] = []
        
#         ticker_dict[ticker].append(close_price)
#     return ticker_dict


date_timestamp = query("SELECT MAX([DATE]) AS Date FROM analytics.TodaySnapshot")["Date"][0]
unique_tickers = query("SELECT COUNT(DISTINCT ticker) AS Count FROM analytics.TodaySnapshot Where SecType = 'Stock'")["Count"][0]
st.caption(f"Looking at {unique_tickers} active tickers from NASDAQ, AMEX, and NYSE. Data as of {date_timestamp}")


mkt_his = query("select * from visual.MktHistogram")
mkt_rank = query("SELECT * from visual.MktRanking")

signals = mkt_his['Signal'].unique()

stock_his = mkt_his[mkt_his["SecType"] == "Stock"]
stock_rank = mkt_rank[mkt_rank["SecType"] == "Stock"]



one, two, three, four = st.columns(4)

for i, signal in enumerate(signals):
    df_stock_his = stock_his[mkt_his["Signal"] == signal]

    df_stock_rank = stock_rank[stock_rank["Signal"] == signal]
    df_stock_rank = df_stock_rank.sort_values(by=['RankGroup','Rank'])
    df_stock_rank['Prices'] = df_stock_rank['Prices'].apply(string_to_array)


    df_stock_rank_highest = df_stock_rank[df_stock_rank["RankGroup"]=="Highest"]
    df_stock_rank_lowest = df_stock_rank[df_stock_rank["RankGroup"]=="Lowest"]
    df_stock_rank_highest = df_stock_rank_highest[['Ticker','Value','Prices','Change','Volume']]
    df_stock_rank_lowest = df_stock_rank_lowest[['Ticker','Value','Prices','Change','Volume']]

    if i == 0:
        column = one
        category_order = {"Bin":["< 0","0 - 12.5","12.5 - 25","25 - 37.5","37.5 - 50","50 - 62.5","62.5 - 75","75 - 87.5","87.5 - 100","> 100"]}
        color_seq = ["#ef4444"] * 5 + ["#22c55e"] * 5
        header = "52 Week Range"
        col_name = "52WkR"
    elif i == 1:
        column = two
        category_order = {"Bin":["< 0","0 - 12.5","12.5 - 25","25 - 37.5","37.5 - 50","50 - 62.5","62.5 - 75","75 - 87.5","87.5 - 100","> 100"]}
        color_seq = ["#ef4444"] * 5 + ["#22c55e"] * 5
        header = "Keltner Channel Position"
        col_name = "KCPos"
    elif i == 2:
        column = three
        category_order = {"Bin":["< -4","-4 - -3","-3 - -2","-2 - -1","-1 - 0","0 - 1","1 - 2","2 - 3","3 - 4","> 4"]}
        color_seq = ["#ef4444"] * 5 + ["#22c55e"] * 5
        header = "Sigma Spike"
        col_name = "SSpike"
    elif i == 3:
        column = four
        category_order = {"Bin":["0 - 1","1 - 2","2 - 3","3 - 4","4 - 5","> 5"]}
        color_seq = ["#0ea5e9"]
        header = "Relative Volume"
        col_name = "RVol"

    with column:
        st.subheader(f"{header}")
        histogram = px.bar(df_stock_his, x ='Bin', y='BinCount', category_orders=category_order, color="Bin", color_discrete_sequence=color_seq,height =400)
        st.plotly_chart(histogram,use_container_width=True)
    
        tab_one, tab_two = st.tabs(["Highest","Lowest"])
        with tab_one:
            df_stock_rank_highest = df_stock_rank_highest.rename(columns = {'Value':col_name})
            st.data_editor(df_stock_rank_highest, 
                           column_config=
                           {"Prices":st.column_config.LineChartColumn("Price",width="small"),
                            "Change":st.column_config.NumberColumn("Change",format="%.2f %%")
                            }, 
                           hide_index=True, 
                           use_container_width=True)
        with tab_two:
            df_stock_rank_lowest = df_stock_rank_lowest.rename(columns = {'Value':col_name})
            st.data_editor(df_stock_rank_lowest, 
                           column_config=
                           {"Prices":st.column_config.LineChartColumn("Price",width="small"),
                            "Change":st.column_config.NumberColumn("Change",format="%.2f %%")
                            }, 
                           hide_index=True, 
                           use_container_width=True)

