import streamlit as st
import plotly.express as px
import config

st.set_page_config(layout="wide", page_title="Stock Analysis", page_icon="📈")
st.markdown(config.condensed_page_style, unsafe_allow_html=True)
config.Navbar()


stock_his = config.query(config.stock_his_query)
stock_rank = config.query(config.stock_ranking_query)

signals = config.signals_sorted

stock_his = stock_his[stock_his["SecType"] == "Stock"]
stock_rank = stock_rank[stock_rank["SecType"] == "Stock"]

st.subheader("Stock Performance")

heatmap, sigma_spike, month_range, year_range, rvol = st.tabs(
    ["Heat Map", "Sigma Spike", "Month Range", "Year Range", "Relative Volume"]
)

for i, signal in enumerate(signals):
    df_stock_his = stock_his[stock_his["Signal"] == signal]

    df_stock_rank = stock_rank[stock_rank["Signal"] == signal]
    df_stock_rank = df_stock_rank.sort_values(by=["RankGroup", "Rank"])
    df_stock_rank["Prices"] = df_stock_rank["Prices"].apply(config.string_to_array)

    df_stock_rank_highest = df_stock_rank[df_stock_rank["RankGroup"] == "Highest"]
    df_stock_rank_lowest = df_stock_rank[df_stock_rank["RankGroup"] == "Lowest"]
    keep_cols = ["Ticker", "Value", "Prices", "Last", "Change", "Volume", "Sector"]
    df_stock_rank_highest = df_stock_rank_highest[keep_cols]
    df_stock_rank_lowest = df_stock_rank_lowest[keep_cols]

    value_count = df_stock_his["BinCount"].sum()
    if i == 0:
        category_order = {"Bin": config.yr_range_bins_sorted}
        color_seq = [config.green] * 5 + [config.red] * 5
        header = "Year Range Distibution"
        col_name = "Year Range"
        tab = year_range
        value_format = "%.2f%%"
    elif i == 1:
        category_order = {"Bin": config.yr_range_bins_sorted}
        color_seq = [config.green] * 5 + [config.red] * 5
        header = "Month Range Distribution"
        col_name = "Month Range"
        tab = month_range
        value_format = "%.2f%%"
    elif i == 2:
        category_order = {"Bin": config.sigma_spike_bins_sorted}
        color_seq = [config.green] * 5 + [config.red] * 5
        header = "Sigma Spike Distribution"
        col_name = "Sigma Spike"
        tab = sigma_spike
        value_format = "%.2f"
    elif i == 3:
        category_order = {"Bin": config.rvol_bins_sorted}
        color_seq = [config.blue]
        header = "Relative Volume Distribution"
        col_name = "Relative Volume"
        tab = rvol
        value_format = "%.2f"

    with tab:
        one, two = st.columns([1, 2])
        with one:
            histogram = px.bar(
                df_stock_his,
                y="Bin",
                x="BinCount",
                category_orders=category_order,
                color="Bin",
                color_discrete_sequence=color_seq,
                labels={"Bin": "Distribution", "BinCount": "Count"},
                text_auto=True,
                title=header,
            )
            histogram.update_layout(margin=dict(t=30), showlegend=False)
            st.write("")
            st.write("")
            st.plotly_chart(histogram, use_container_width=True)
        with two:
            df_stock_rank_highest = df_stock_rank_highest.rename(
                columns={"Value": col_name}
            )
            df_stock_rank_lowest = df_stock_rank_lowest.rename(
                columns={"Value": col_name}
            )

            tab_one, tab_two = st.tabs(["Highest", "Lowest"])
            with tab_one:
                st.data_editor(
                    df_stock_rank_highest,
                    column_config={
                        "Prices": st.column_config.LineChartColumn(
                            "21 Day Chart", width="small"
                        ),
                        "Change": st.column_config.NumberColumn(
                            "Change", format="%.2f%%"
                        ),
                        col_name: st.column_config.NumberColumn(
                            col_name, format=value_format
                        ),
                    },
                    hide_index=True,
                    disabled=True,
                    use_container_width=True,
                )
            with tab_two:
                st.data_editor(
                    df_stock_rank_lowest,
                    column_config={
                        "Prices": st.column_config.LineChartColumn(
                            "21 Day Chart", width="small"
                        ),
                        "Change": st.column_config.NumberColumn(
                            "Change", format="%.2f%%"
                        ),
                    },
                    hide_index=True,
                    disabled=True,
                    use_container_width=True,
                )

with heatmap:
    heatmap_data = config.query(config.stock_heatmap_query)
    heatmap_data["Return"] = heatmap_data["Return"] * 100
    heatmap_data = heatmap_data.sort_values(by="Ticker")

    heatmap_plot = px.treemap(
        heatmap_data,
        path=[
            px.Constant("Stock Heatmap (Sigma Spike)"),
            "Sector",
            "Industry",
            "Ticker",
        ],
        values="MarketCap",
        color="SigmaSpike",
        color_continuous_scale=[config.red] * 5
        + [config.darkgrey]
        + [config.green] * 5,
        color_continuous_midpoint=0,
    )
    heatmap_plot.update_layout(margin=dict(t=0, b=0, r=0), height=650, font_size=15)

    heatmap_plot.update_coloraxes(showscale=False)
    heatmap_plot.data[0].customdata = heatmap_data[
        ["Ticker", "SigmaSpike", "Return"]
    ].round(
        2
    )  # round to 2 decimal places
    heatmap_plot.data[0].texttemplate = "%{label}<br>%{customdata[1]}"
    heatmap_plot.update_traces(
        textposition="middle center",
        marker=dict(cornerradius=3),
        hovertemplate="<b>%{label} </b> <br> Sigma Spike: %{color:.2f} <br> Return: %{customdata[2]:.2f}%",
    )
    st.plotly_chart(heatmap_plot, use_container_width=True)


date_timestamp = config.query(config.timestamp_query)["Date"][0]
unique_tickers = config.query(config.unique_tickers_query)["Count"][0]
st.caption(
    f"Looking at {unique_tickers} active tickers from NASDAQ, AMEX, and NYSE. EOD Data as of {date_timestamp}"
)
