import streamlit as st
import json
import pandas as pd
import requests
import numpy as np
import plotly.graph_objects as go
from st_pages import show_pages_from_config

st.set_page_config(layout="wide")


show_pages_from_config()
# Define the URL and payload for the POST request
url =  st.secrets["DB_URL"]

@st.cache_data(ttl = 3600)
def query(query):
    request = {"query": query}
    response = json.loads(requests.post(url, json=request).content.decode('utf-8'))
    return pd.DataFrame(response)




index_prices_query = "select  P.Ticker, T.Name,[Date], [Open], [High], [Low], [Close], Volume \
    from raw.Prices P Left Join raw.Tickers T on P.Ticker = T.Ticker \
        where T.SecType = 'Index'\
            AND [Date] >= DATEADD(month, -2, GETDATE())"

index_prices = query(index_prices_query)
tickers= ['^GSPC', '^RUT', '^IXIC', '^GSPTSE', '^VIX','^DXY','^FVX','^TYX'] ## exclude '^TNX'

# Calculate the number of tickers per column
tickers_per_column = int(np.ceil(len(tickers) / 2))


st.subheader('Index Performance')
columns = st.columns(4)

# Iterate over tickers and display DataFrame for each ticker in a separate column
for i, ticker in enumerate(tickers):
    column_index = i % tickers_per_column  # Calculate the column index based on the ticker index

    with columns[column_index]:
        index = index_prices[index_prices['Ticker'] == ticker]
        index_name = index['Name'].iloc[0]
        candlestick_chart = go.Figure(data=[go.Candlestick(
                                                x=index['Date'],
                                                open = index['Open'],
                                                high = index['High'],
                                                low=index['Low'],
                                                close=index['Close'],
                                                increasing_line_color = "#22c55e",
                                                increasing_fillcolor = "#22c55e",
                                                decreasing_line_color = "#ef4444",
                                                decreasing_fillcolor = "#ef4444"
                                                )])
        candlestick_chart.update_layout(
            title = index_name,
            xaxis_rangeslider_visible=False)
        candlestick_chart.update_xaxes(
            rangebreaks=[dict(bounds=["sat", "mon"])]
            )
        st.plotly_chart(candlestick_chart, use_container_width=True)

st.divider()

st.subheader('One-Day Returns')
market_sum_query = "SELECT S.Ticker, S.SecType, SigmaSpike, Name FROM analytics.TodaySnapShot S\
     Left Join raw.Tickers T on T.Ticker=S.Ticker\
          WHERE S.SecType = 'ETF'"
market_sum = query(market_sum_query)
# add conditional color
market_sum["Color"] = np.where(market_sum["SigmaSpike"]<0, '#ef4444', '#22c55e')

market_etf = ['SPY','QQQ','IWM']
sector_etf = ['XLC','XLY','XLP','XLE','XLF','XLV','XLI','XLB','XLRE','XLK','XLU']
country_etf = ['GXC','EWZ','EWJ','EWU','EWC','PIN','VNM']

etf_order = market_etf + sector_etf + country_etf

market_sum['Ticker'] = pd.Categorical(market_sum['Ticker'], categories=etf_order, ordered=True)
market_sum = market_sum.sort_values('Ticker')

bar_chart = go.Figure(data=[go.Bar(
                            x = market_sum['Ticker'],
                            y = market_sum['SigmaSpike'],
                            marker_color = market_sum['Color']
                            )])

bar_chart.add_vline(x=2.5, line_width=1, line_dash="dash", line_color="grey")
bar_chart.add_vline(x=13.5, line_width=1, line_dash="dash", line_color="grey")

# make space for explanation / annotation
bar_chart.update_layout(margin=dict(t=50))


# add annotation
bar_chart.add_annotation(dict(font=dict(color='white',size=15),
                                        x=0.07,
                                        y=1.1,
                                        showarrow=False,
                                        text="US Stocks",
                                        textangle=0,
                                        xanchor='center',
                                        xref="paper",
                                        yref="paper"))
bar_chart.add_annotation(dict(font=dict(color='white',size=15),
                                        x=0.405,
                                        y=1.1,
                                        showarrow=False,
                                        text="US Sectors",
                                        textangle=0,
                                        xanchor='center',
                                        xref="paper",
                                        yref="paper"))
bar_chart.add_annotation(dict(font=dict(color='white',size=15),
                                        x=0.83,
                                        y=1.1,
                                        showarrow=False,
                                        text="Ex-US Stocks",
                                        textangle=0,
                                        xanchor='center',
                                        xref="paper",
                                        yref="paper"))

bar_chart.update_layout(height=300)
st.plotly_chart(bar_chart, use_container_width=True)



date_timestamp = query("SELECT MAX([DATE]) AS Date FROM analytics.TodaySnapshot")["Date"][0]
st.caption(f"Looking at major US indexes and ETFs. Data as of {date_timestamp}")
