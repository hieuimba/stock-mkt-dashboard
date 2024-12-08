import streamlit as st
import config

st.set_page_config(layout="wide", page_title="Glossary", page_icon="📈")
st.markdown(config.condensed_page_style, unsafe_allow_html=True)

config.Navbar()

st.subheader("Sigma Spike")
st.write(
    "Sigma Spike is an indicator used to identify significant deviations in prices. \
         It compares today's return (percentage change in price) to the standard deviation of past returns."
)
st.write(
    "A higher sigma spike indicates a larger and potentially abnormal price movement, while a lower value suggests a more typical change."
)
st.write(
    "Sigma Spike is used when comparing returns between different markets as it accounts for their different volatility levels."
)
st.caption(
    "Sigma Spike was orignally coined by trader Adam Grimes. Learn more about it here: https://adamhgrimes.com/how-to-calculate-sigmaspikes/"
)
st.latex(
    r"""
\text{{Sigma Spike}} = \frac{{\text{{Today's return}}}}{{\text{{Yesterday's standard deviation (21 periods)}}}}
    """
)

st.subheader("Month Range")
st.write(
    "A Keltner Channel with a 21-bar daily period represents a range of expected price volatility over a one-month timeframe."
)
st.write(
    "It consists of an upper band, lower band, and a middle band. The upper and lower bands expand or contract based on market volatility, indicating potential price extremes. "
)
st.write(
    "If the close of the asset approaches or exceeds the upper band, it may suggest overbought conditions, while reaching or falling below the lower band may indicate oversold conditions."
)
st.latex(
    r"""
\text{Keltner Channel Middle Line} = \text{EMA}
         """
)
st.latex(
    r"""
\text{Keltner Channel Upper Band} = \text{EMA} + 2.5 \times \text{ATR}
         """
)
st.latex(
    r"""
\text{Keltner Channel Lower Band} = \text{EMA} - 2.5 \times \text{ATR}
         """
)
st.latex(
    r"""
where:
         """
)
st.latex(
    r"""
\text{EMA} = \text{Exponential moving average (21 periods)}
         """
)
st.latex(
    r"""
\text{ATR} = \text{Average True Range (21 periods)}
    """
)


st.subheader("Year Range")
st.write(
    "The 52-week high and low range represents the highest and lowest prices a stock or asset has reached over the past year."
)
st.write(
    "The year range provides a measure of the stock's volatility and its relative performance."
)
st.write(
    "When an asset is near or at its 52-week high, it suggests strength or bullish sentiment, while being closer to the 52-week low indicates weakness or bearish sentiment."
)
st.latex(
    r"""
\text{52-week High} = \max(\text{Closing prices over the past 52 weeks})
    """
)
st.latex(
    r"""
\text{52-week Low} = \min(\text{Closing prices over the past 52 weeks})
    """
)

st.subheader("Relative Volume (Rvol)")
st.write(
    "Relative Volume is a measure used to evaluate the trading activity of a stock in relation to its average volume."
)
st.write(
    "By comparing today's volume to the 21-day exponential moving average (yesterday's volume EMA), Relative Volume indicates whether the current volume is higher or lower than usual."
)
st.write(
    "A value above 1 suggests increased activity, while a value below 1 indicates decreased activity, providing insights into market interest and potential price movements."
)
st.latex(
    r"""
\text{Relative Volume} = \frac{\text{Today's volume}}{\text{Yesterday's volume EMA (21 periods)}}
    """
)
