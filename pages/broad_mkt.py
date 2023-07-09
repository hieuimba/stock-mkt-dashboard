import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import config
from st_pages import show_pages_from_config

st.set_page_config(layout="wide")
show_pages_from_config()
st.markdown(config.condensed_page_style, unsafe_allow_html=True)


st.subheader('Broad Market Performance')
charts, index_summary, one_day_returns = st.tabs(["Index Charts","Index Summary","One-Day Returns"])

keep_indexes= ['^GSPC', '^IXIC', '^RUT', '^GSPTSE', '^VIX','^DXY','^FVX','^TYX'] ## exclude '^TNX'

with charts:
    index_prices_query = config.index_prices_query
    index_prices = config.query(index_prices_query)

    # Calculate the number of tickers per column
    tickers_per_column = int(np.ceil(len(keep_indexes) / 2))
    columns = st.columns(4)

    # Iterate over tickers and display DataFrame for each ticker in a separate column
    for i, ticker in enumerate(keep_indexes):
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
                                                    increasing_line_color = config.green,
                                                    increasing_fillcolor = config.green,
                                                    decreasing_line_color = config.red,
                                                    decreasing_fillcolor = config.red
                                                    )])
            candlestick_chart.update_layout(
                margin=dict(t=30,b=30,r=30),
                height = 300,
                title = index_name,
                xaxis_rangeslider_visible=False)
            candlestick_chart.update_xaxes(
                rangebreaks=[dict(bounds=["sat", "mon"])]
                )
            st.plotly_chart(candlestick_chart, use_container_width=True)
with index_summary:
    index_summary_table = config.query(config.index_table_query)
    index_summary_table = index_summary_table.loc[index_summary_table['Ticker'].isin(keep_indexes)].sort_values(by=['Ticker'], key=lambda x: x.map({v: i for i, v in enumerate(keep_indexes)}))


    index_summary_table = index_summary_table.rename(
        columns={old_col: new_col for old_col, new_col in zip(config.sum_table_rename_source, config.sum_table_rename_target)}
    )
    st.dataframe(index_summary_table.style.format({col: '{:.2%}' if col != 'Sigma Spike' else '{:.2}'for col in config.sum_table_percentage_format_subset})
                 .applymap(config.format_positive_negative_cell_color, subset=config.sum_table_color_format_subset), 
                hide_index=True,
                use_container_width=True)


with one_day_returns:
    market_sum = config.query(config.one_day_return_query)
    # add conditional color
    market_sum['Color'] = np.where(market_sum["SigmaSpike"]<0, config.red, config.green)
    market_sum['SigmaSpike'] = market_sum['SigmaSpike'].round(2)

    market_etf = ['SPY','QQQ','IWM']
    sector_etf = sorted(['XLC','XLY','XLP','XLE','XLF','XLV','XLI','XLB','XLRE','XLK','XLU'])
    country_etf = sorted(['GXC','EWZ','EWJ','EWU','EWC','PIN','VNM'])

    etf_order = market_etf + sector_etf + country_etf

    market_sum['Ticker'] = pd.Categorical(market_sum['Ticker'], categories=etf_order, ordered=True)
    market_sum = market_sum.sort_values('Ticker')
    market_sum['Name'] = market_sum['ShortName'] + ' (' + market_sum['Ticker'].astype(str) + ')'

    bar_chart = go.Figure(data=[go.Bar(
                                x = market_sum['ShortName'],
                                y = market_sum['SigmaSpike'],
                                marker_color = market_sum['Color']
                                )])

    bar_chart.add_vline(x=2.5, line_width=1, line_dash="dash", line_color="grey")
    bar_chart.add_vline(x=13.5, line_width=1, line_dash="dash", line_color="grey")
    bar_chart.update_traces(text = market_sum['SigmaSpike'], textposition= 'auto')

    # make space for explanation / annotation
    bar_chart.update_layout(margin=dict(t=50), 
                            bargap = 0.5)


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

    bar_chart.update_layout(height=400)
    st.plotly_chart(bar_chart, use_container_width=True)



date_timestamp = config.query(config.timestamp_query)["Date"][0]
st.caption(f"Looking at major US indexes and ETFs. Data as of {date_timestamp}")
