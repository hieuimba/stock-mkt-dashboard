import streamlit as st
import config
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(layout="wide")
st.markdown(config.condensed_page_style, unsafe_allow_html=True)


etf_prices = config.query(config.etf_prices_query)


def create_etf_chart(df):
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
                    etf_df = df[df['Ticker'] == ticker].copy()

                    etf_df['Return'] = (etf_df['Return']*100).round(2)
                    return_value =  etf_df['Return'].iloc[-1]
                    return_str = f"+{return_value}%" if return_value >= 0 else f"{return_value}%"
                    return_color = config.red if return_value <0 else config.green

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
                        margin=dict(t=30, b=30, r=30),
                        height = 300,
                        title = title,
                        xaxis_rangeslider_visible=False)
                    candlestick_chart.update_xaxes(
                        rangebreaks=[dict(bounds=["sat", "mon"])]
                        )
                    # Add return_str as text in the top right corner
                    candlestick_chart.add_annotation(
                        x=1,
                        y=1.13,
                        text=return_str,
                        font=dict(color=return_color, size=15),
                        showarrow=False,
                        align='right',
                        xref='paper',
                        yref='paper'
                    )
                    st.plotly_chart(candlestick_chart, use_container_width=True)

st.subheader("Sector Performance")

charts, etf_summary, etf_correlation = st.tabs(["Charts","Summary","Sector Correlations"])

with charts:
    create_etf_chart(etf_prices)

with etf_summary:
    etf_summary_table = config.query(config.etf_table_query)
    etf_summary_table = etf_summary_table.rename(
        columns={old_col: new_col for old_col, new_col in zip(config.sum_table_rename_source, config.sum_table_rename_target)}
    )
    etf_summary_table['Name'] = etf_summary_table['Name'].str.split('Select').str[0].str.strip()
    etf_summary_table.loc[etf_summary_table['Name'] == 'The Real Estate', 'Name'] = 'Real Estate'
    st.dataframe(etf_summary_table.style.format({col: '{:.2%}' if col != 'Sigma Spike' else '{:.2}'for col in config.sum_table_percentage_format_subset})
                 .applymap(config.format_positive_negative_cell_color, subset=config.sum_table_color_format_subset), 
                hide_index=True,
                height=(11+1)*35+3,
                use_container_width=True)

with etf_correlation:
    one_month, one_year = st.columns(2)
    with one_month:
        etf_return = config.query(config.etf_return_query_one_month_query)
        etf_return['Name'] = etf_return['Name'].str.split('Select').str[0].str.strip()

        correlation_matrix_data = etf_return.pivot(columns='Name', values='Return', index='Order').corr().round(2)

        correlation_matrix_plot = px.imshow(correlation_matrix_data,
                                            text_auto=True, 
                                            aspect="auto",
                                            labels=dict(x="Sector", y="Sector"),
                                            color_continuous_scale=[config.red, config.darkgrey,config.darkgrey, config.green])
        correlation_matrix_plot.update_coloraxes(showscale=False)
        correlation_matrix_plot.update_layout(
            margin=dict(t=30),
            height = 650,
            title = 'One Month Correlation')
        
        st.plotly_chart(correlation_matrix_plot,use_container_width=True)
    with one_year:
        etf_return = config.query(config.etf_return_query_one_year_query)
        etf_return['Name'] = etf_return['Name'].str.split('Select').str[0].str.strip()

        correlation_matrix_data = etf_return.pivot(columns='Name', values='Return', index='Order').corr().round(2)
        correlation_matrix_plot = px.imshow(correlation_matrix_data,
                                            text_auto=True, 
                                            aspect="auto",
                                            labels=dict(x="Sector", y="Sector"),
                                            color_continuous_scale=[config.red, config.darkgrey,config.darkgrey, config.green])
        correlation_matrix_plot.update_layout(
            margin=dict(t=30),
            height = 650,
            title = 'One Year Correlation')
        correlation_matrix_plot.update_coloraxes(showscale=False)
        
        st.plotly_chart(correlation_matrix_plot,use_container_width=True)


date_timestamp = config.query(config.timestamp_query)["Date"][0]
st.caption(f"Looking at 11 market sector ETFs. EOD Data as of {date_timestamp}")