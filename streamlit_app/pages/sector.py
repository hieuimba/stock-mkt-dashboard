import streamlit as st
import config
import plotly.graph_objects as go
import plotly.express as px
import re


st.set_page_config(layout="wide", page_title="Sector Analysis", page_icon="📈")
st.markdown(config.condensed_page_style, unsafe_allow_html=True)

config.Navbar()

st.subheader("Sector Performance")

charts, sector_summary, sector_correlation = st.tabs(
    ["Charts", "Summary", "Sector Correlations"]
)

with charts:
    sector_prices = config.query(config.sector_prices_query)
    tickers = sector_prices["Ticker"].unique()
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
                    sector_df = sector_prices[sector_prices["Ticker"] == ticker].copy()

                    sector_df["Return"] = (sector_df["Return"] * 100).round(2)
                    return_value = sector_df["Return"].iloc[-1]
                    return_str = (
                        f"+{return_value}%" if return_value >= 0 else f"{return_value}%"
                    )
                    return_color = config.red if return_value < 0 else config.green

                    title = (
                        f"{sector_df['Name'].iloc[0]} ({sector_df['Ticker'].iloc[0]})"
                    )

                    candlestick_chart = go.Figure(
                        data=[
                            go.Candlestick(
                                x=sector_df["Date"],
                                open=sector_df["Open"],
                                high=sector_df["High"],
                                low=sector_df["Low"],
                                close=sector_df["Close"],
                                increasing_line_color=config.green,
                                increasing_fillcolor=config.green,
                                decreasing_line_color=config.red,
                                decreasing_fillcolor=config.red,
                            )
                        ]
                    )
                    candlestick_chart.update_layout(
                        margin=dict(t=30, b=30, r=30),
                        height=300,
                        title=title,
                        xaxis_rangeslider_visible=False,
                    )
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
                        align="right",
                        xref="paper",
                        yref="paper",
                    )
                    st.plotly_chart(candlestick_chart, use_container_width=True)

with sector_summary:
    sector_summary_table = config.query(config.sector_table_query)
    sector_summary_table = sector_summary_table.drop(["Updated", "SecType"], axis=1)
    sector_summary_table["MonthRange"] = sector_summary_table["MonthRange"] / 100
    sector_summary_table["YearRange"] = sector_summary_table["YearRange"] / 100

    sector_summary_table.columns = [
        re.sub(r"(?<!^)(?=[A-Z])", config.add_space, column)
        for column in sector_summary_table.columns.tolist()
    ]

    sector_summary_table["Name"] = (
        sector_summary_table["Name"].str.split("Select").str[0].str.strip()
    )
    sector_summary_table.loc[
        sector_summary_table["Name"] == "The Real Estate", "Name"
    ] = "Real Estate"

    percentage_format_subset = [
        i for i in sector_summary_table.columns.tolist() if i not in ["Name", "Ticker"]
    ]
    color_format_subset = [
        i
        for i in sector_summary_table.columns.tolist()
        if i not in ["Name", "Ticker", "Month Range", "Year Range"]
    ]

    st.dataframe(
        sector_summary_table.style.format(
            {
                col: "{:.2%}" if col != "Sigma Spike" else "{:.2}"
                for col in percentage_format_subset
            }
        ).applymap(
            config.format_positive_negative_cell_color, subset=color_format_subset
        ),
        hide_index=True,
        height=(11 + 1) * 35 + 3,
        use_container_width=True,
    )

with sector_correlation:
    one_month, one_year = st.columns(2)
    sector_return = config.query(config.sector_return_query)
    sector_return["Name"] = sector_return["Name"].str.split("Select").str[0].str.strip()
    sector_return_one_month = sector_return[sector_return["Order"] <= 20]

    with one_month:
        correlation_matrix_data = (
            sector_return_one_month.pivot(
                columns="Name", values="Return", index="Order"
            )
            .corr()
            .round(2)
        )

        correlation_matrix_plot = px.imshow(
            correlation_matrix_data,
            text_auto=True,
            aspect="auto",
            labels=dict(x="Sector", y="Sector"),
            color_continuous_scale=[
                config.red,
                config.darkgrey,
                config.darkgrey,
                config.green,
            ],
        )
        correlation_matrix_plot.update_coloraxes(showscale=False)
        correlation_matrix_plot.update_layout(
            margin=dict(t=30), height=650, title="One Month Correlation"
        )

        st.plotly_chart(correlation_matrix_plot, use_container_width=True)
    with one_year:
        correlation_matrix_data = (
            sector_return.pivot(columns="Name", values="Return", index="Order")
            .corr()
            .round(2)
        )
        correlation_matrix_plot = px.imshow(
            correlation_matrix_data,
            text_auto=True,
            aspect="auto",
            labels=dict(x="Sector", y="Sector"),
            color_continuous_scale=[
                config.red,
                config.darkgrey,
                config.darkgrey,
                config.green,
            ],
        )
        correlation_matrix_plot.update_layout(
            margin=dict(t=30), height=650, title="One Year Correlation"
        )
        correlation_matrix_plot.update_coloraxes(showscale=False)

        st.plotly_chart(correlation_matrix_plot, use_container_width=True)


date_timestamp = config.query(config.timestamp_query)["Date"][0]
st.caption(f"Looking at 11 US sector ETFs. EOD Data as of {date_timestamp}")
