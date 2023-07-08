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


mkt_his = query("select * from visual.StockHistogram")
mkt_rank = query("SELECT * from visual.StockRanking")

signals = ['52WkRange', 'KCPos', 'SigmaSpike','RVol']

stock_his = mkt_his[mkt_his["SecType"] == "Stock"]
stock_rank = mkt_rank[mkt_rank["SecType"] == "Stock"]




for i, signal in enumerate(signals):
    df_stock_his = stock_his[mkt_his["Signal"] == signal]

    df_stock_rank = stock_rank[stock_rank["Signal"] == signal]
    df_stock_rank = df_stock_rank.sort_values(by=['RankGroup','Rank'])
    df_stock_rank['Prices'] = df_stock_rank['Prices'].apply(string_to_array)

    df_stock_rank_highest = df_stock_rank[df_stock_rank["RankGroup"]=="Highest"]
    df_stock_rank_lowest = df_stock_rank[df_stock_rank["RankGroup"]=="Lowest"]
    df_stock_rank_highest = df_stock_rank_highest[['Ticker','Value','Prices','Last','Change','Volume','Sector']]
    df_stock_rank_lowest = df_stock_rank_lowest[['Ticker','Value','Prices','Last','Change','Volume','Sector']]

    value_count = df_stock_his["BinCount"].sum()
    if i == 0:
        category_order = {"Bin":["> 100", "87.5 - 100", "75 - 87.5", "62.5 - 75", "50 - 62.5", "37.5 - 50", "25 - 37.5", "12.5 - 25", "0 - 12.5", "< 0"]}
        color_seq =  ["#22c55e"] * 5 + ["#ef4444"] * 5 
        header = "Year Range"
        col_name = "52 Week Range"

    elif i == 1:
        category_order = {"Bin":["> 100", "87.5 - 100", "75 - 87.5", "62.5 - 75", "50 - 62.5", "37.5 - 50", "25 - 37.5", "12.5 - 25", "0 - 12.5", "< 0"]}
        color_seq = ["#22c55e"] * 5 + ["#ef4444"] * 5 
        header = "Month Range"
        col_name = "KC Position"

    elif i == 2:
        category_order = {"Bin":["> 4", "3 - 4", "2 - 3", "1 - 2", "0 - 1", "-1 - 0", "-2 - -1", "-3 - -2", "-4 - -3", "< -4"]}
        color_seq = ["#22c55e"] * 5 +  ["#ef4444"] * 5 
        header = "Relative Return"
        col_name = "Sigma Spike"

    elif i == 3:
        category_order = {"Bin":["> 5", "4 - 5", "3 - 4", "2 - 3", "1 - 2", "0 - 1"]}
        color_seq = ["#0ea5e9"]
        header = "Relative Volume"
        col_name = "Relative Volume"


    
    one, two = st.columns([1,2])


    with one:
        st.subheader(f"{header}")
        histogram = px.bar(df_stock_his, 
                           y ='Bin', 
                           x='BinCount', 
                           category_orders=category_order, 
                           color="Bin", 
                           color_discrete_sequence=color_seq,
                           height =400,
                           labels={'Bin':'Distribution', 'BinCount':'Count'},
                           text_auto=True
                           )
        histogram.update_layout(showlegend=False)
        st.plotly_chart(histogram,use_container_width=True)
    with two:
        tab_one, tab_two = st.tabs(["Highest","Lowest"])
        with tab_one:
            df_stock_rank_highest = df_stock_rank_highest.rename(columns = {'Value':col_name})
            st.data_editor(df_stock_rank_highest, 
                           height = 388,
                           column_config=
                           {"Prices":st.column_config.LineChartColumn("21 Day Chart",width="small"),
                            "Change":st.column_config.NumberColumn("Change",format="%.2f %%")
                            }, 
                           hide_index=True, 
                           disabled= True,
                           use_container_width=True)
        with tab_two:
            df_stock_rank_lowest = df_stock_rank_lowest.rename(columns = {'Value':col_name})
            st.data_editor(df_stock_rank_lowest, 
                           height = 400,
                           column_config=
                           {"Prices":st.column_config.LineChartColumn("21 Day Chart",width="small"),
                            "Change":st.column_config.NumberColumn("Change",format="%.2f %%")
                            }, 
                           hide_index=True, 
                           disabled= True,
                           use_container_width=True)


date_timestamp = query("SELECT MAX([DATE]) AS Date FROM analytics.TodaySnapshot")["Date"][0]
unique_tickers = query("SELECT COUNT(DISTINCT ticker) AS Count FROM analytics.TodaySnapshot Where SecType = 'Stock'")["Count"][0]
st.caption(f"Looking at {unique_tickers} active tickers from NASDAQ, AMEX, and NYSE. Data as of {date_timestamp}")
