import streamlit as st
import config
import pandas as pd
import plotly.graph_objects as go


st.set_page_config(layout="wide")


etf_prices = config.query(config.etf_prices_query)


def create_tables(df):
    tickers = df['Ticker'].unique()
    num_tickers = len(tickers)
    num_cols = 4
    num_rows = (num_tickers + num_cols - 1) // num_cols

    # Create tables in the specified layout
    for i in range(num_rows):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            ticker_index = i * num_cols + j
            if ticker_index < num_tickers:
                ticker = tickers[ticker_index]
                with cols[j]:
                    etf_df = df[df['Ticker'] == ticker]
                    title = f"{etf_df['Name'].iloc[0]} ({etf_df['Ticker'].iloc[0]})"
                    
                    candlestick_chart = go.Figure(data=[go.Candlestick(
                                            x=etf_df['Date'],
                                            open = etf_df['Open'],
                                            high = etf_df['High'],
                                            low=etf_df['Low'],
                                            close=etf_df['Close'],
                                            increasing_line_color = config.green,
                                            increasing_fillcolor = config.green,
                                            decreasing_line_color = config.red,
                                            decreasing_fillcolor = config.red
                                            )])
                    candlestick_chart.update_layout(
                        margin=dict(t=30, b=30),
                        height = 330,
                        title = title,
                        xaxis_rangeslider_visible=False)
                    candlestick_chart.update_xaxes(
                        rangebreaks=[dict(bounds=["sat", "mon"])]
                        )
                    st.plotly_chart(candlestick_chart, use_container_width=True)

st.subheader("Sector Performance")
create_tables(etf_prices)

st.subheader("Sector Correlation Matrix")