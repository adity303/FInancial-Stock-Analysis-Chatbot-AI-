import streamlit as st
import plotly.graph_objects as go
from stock_utils import get_stock_price, get_stock_history
from chatbot import chatbot_response

# Page Config - Streamlit
st.set_page_config(page_title="Stock Assistant", layout="wide")

st.title("📈 Financial Stock Assistant Chatbot")

# Sidebar Menu
menu = st.sidebar.radio(
    "Choose View",
    ["Price", "Chart", "Compare", "Chatbot"]
)

# Common Inputs
ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL")
period = st.sidebar.selectbox(
    "Select Period",
    ["1mo", "3mo", "6mo", "1y", "2y"]
)

# ---------------- PRICE VIEW ----------------
if menu == "Price":

    if st.sidebar.button("Get Stock Data"):
        data = get_stock_price(ticker)

        st.subheader("📊 Stock Details")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Company", data["name"])
        col2.metric("Price", data["price"])
        col3.metric("Market Cap", data["marketCap"])
        col4.metric("PE Ratio", data["peRatio"])

# ---------------- CHART VIEW ----------------
elif menu == "Chart":

    if st.sidebar.button("Show Chart"):

        hist = get_stock_history(ticker, period)

        st.subheader(f"📉 {ticker} Price Chart ({period})")

        # Line Chart
        st.write("### Line Chart")
        st.line_chart(hist["Close"])

        # Bar Chart
        st.write("### Volume Chart")
        st.bar_chart(hist["Volume"])

        # Candlestick Chart
        fig = go.Figure(data=[
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"]
            )
        ])

        fig.update_layout(
            title="Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price"
        )

        st.plotly_chart(fig, use_container_width=True)
        

# ---------------- COMPARE VIEW ----------------
elif menu == "Compare":

    st.subheader("📊 Compare Two Stocks")

    col1, col2 = st.columns(2) # Two columns for input

    with col1:
        ticker1 = st.text_input("Enter First Stock", "AAPL")

    with col2:
        ticker2 = st.text_input("Enter Second Stock", "TSLA")

    if st.button("Compare Stocks"): # condition for comparison

        data1 = get_stock_price(ticker1)
        data2 = get_stock_price(ticker2)

        st.write("## Comparison Result")

        c1, c2 = st.columns(2) # Two columns for comparison results

        # First Stock
        with c1:
            st.markdown(f"### {ticker1}")
            st.metric("Company", data1["name"])
            st.metric("Price", data1["price"])
            st.metric("Market Cap", data1["marketCap"])
            st.metric("PE Ratio", data1["peRatio"])

        # Second Stock
        with c2:
            st.markdown(f"### {ticker2}")
            st.metric("Company", data2["name"])
            st.metric("Price", data2["price"])
            st.metric("Market Cap", data2["marketCap"])
            st.metric("PE Ratio", data2["peRatio"])

    hist1 = get_stock_history(ticker1, "6mo")
    hist2 = get_stock_history(ticker2, "6mo")

    st.write("## Closing price comparision (6 months)")

    chart_data = {
    ticker1: hist1["Close"],
    ticker2: hist2["Close"]
    }

    # Line Chart
    st.line_chart(chart_data)
    # Bar chart 
    st.bar_chart(chart_data)
    # Area chart
    st.area_chart(chart_data)


# ---------------- CHATBOT VIEW ----------------
elif menu == "Chatbot":

    st.subheader("💬 Ask Financial Questions")

    user_input = st.text_input("Type your question")

    if st.button("Send"):
        reply = chatbot_response(user_input)
        st.success(reply)