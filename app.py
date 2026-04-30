import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime
from stock_utils import get_stock_price, get_stock_history, get_stock_with_change, get_stock_trend, get_correlation_matrix
from chatbot import chatbot_response
from portfolio_utils import generate_portfolio_recommendation, get_portfolio_description, get_suggested_instruments
from news_utils import get_trending_companies, get_market_news, stock_news
from auth import init_auth, is_authenticated, login, signup, logout, get_current_user_id, get_current_username, require_auth
from database import add_to_watchlist, remove_from_watchlist, get_watchlist, is_in_watchlist, save_portfolio, get_user_portfolios, get_portfolio, delete_portfolio

# Page Config - Streamlit
st.set_page_config(page_title="Stock Assistant", layout="wide", page_icon="📈")

# Initialize authentication
init_auth()

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .dashboard-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .watchlist-ticker {
        display: inline-block;
        background: #e3f2fd;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-weight: bold;
        color: #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - User Auth Section
st.sidebar.markdown("---")

if is_authenticated():
    user_id = get_current_user_id()
    username = get_current_username()
    st.sidebar.success(f"👤 Logged in as: **{username}**")

    # Logout button
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    # Get user's watchlist count
    watchlist = get_watchlist(user_id)
    st.sidebar.info(f"📌 Watchlist: {len(watchlist)} stocks")

else:
    st.sidebar.warning("🔒 Not logged in")
    st.sidebar.info("Sign up/Login to save watchlists and portfolios")

st.sidebar.markdown("---")

# Define menu based on authentication
if is_authenticated():
    menu_options = ["Price", "Chart", "Compare", "Correlation Heatmap", "Chatbot", "Analysis",
                    "Portfolio Recommendation", "News Intelligence", "Dashboard", "Watchlist"]
else:
    menu_options = ["Price", "Chart", "Compare", "Correlation Heatmap", "Chatbot", "Analysis",
                    "Portfolio Recommendation", "News Intelligence", "Login/Signup"]

menu = st.sidebar.radio("Choose View", menu_options)

# Common Inputs (only show for authenticated pages that need them)
if menu not in ["Dashboard", "Watchlist", "Login/Signup"]:
    ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL")
    period = st.sidebar.selectbox(
        "Select Period",
        ["1mo", "3mo", "6mo", "1y", "2y"]
    )

# ==================== LOGIN/SIGNUP PAGE ====================
if menu == "Login/Signup":
    st.markdown('<div class="main-header">🔐 Authentication</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔑 Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", key="login_btn"):
            success, message = login(login_username, login_password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col2:
        st.markdown("### 📝 Sign Up")
        signup_username = st.text_input("Choose Username", key="signup_username")
        signup_email = st.text_input("Email Address", key="signup_email")
        signup_password = st.text_input("Choose Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Create Account", type="primary", key="signup_btn"):
            if signup_password != signup_confirm:
                st.error("Passwords do not match!")
            else:
                success, message = signup(signup_username, signup_email, signup_password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("---")
    st.info("""
    **Why create an account?**
    - ✅ Save your watchlist
    - ✅ Store portfolio recommendations
    - ✅ Access your data from anywhere
    - ✅ Personalized financial dashboard
    """)

# ==================== DASHBOARD PAGE ====================
elif menu == "Dashboard":
    if not require_auth():
        st.stop()

    st.markdown('<div class="main-header">📊 User Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Welcome back, {get_current_username()}!</div>', unsafe_allow_html=True)

    user_id = get_current_user_id()

    # Dashboard stats
    col1, col2, col3 = st.columns(3)

    with col1:
        watchlist_count = len(get_watchlist(user_id))
        st.metric("📌 Watchlist Stocks", watchlist_count)

    with col2:
        portfolios = get_user_portfolios(user_id)
        st.metric("💼 Saved Portfolios", len(portfolios))

    with col3:
        st.metric("📈 Account Status", "Active")

    st.markdown("---")

    # Quick Actions
    st.markdown("## ⚡ Quick Actions")
    q_col1, q_col2, q_col3 = st.columns(3)

    with q_col1:
        if st.button("📌 View Watchlist", use_container_width=True):
            st.session_state['menu'] = "Watchlist"
            st.rerun()

    with q_col2:
        if st.button("🧠 New Portfolio", use_container_width=True):
            st.session_state['menu'] = "Portfolio Recommendation"
            st.rerun()

    with q_col3:
        if st.button("📰 Check News", use_container_width=True):
            st.session_state['menu'] = "News Intelligence"
            st.rerun()

    st.markdown("---")

    # Recent Activity
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("## 💼 Recent Portfolios")
        user_portfolios = get_user_portfolios(user_id)[:3]  # Show last 3

        if user_portfolios:
            for pf in user_portfolios:
                with st.expander(f"📁 {pf['name']} - ₹{pf['budget']:,.0f}"):
                    st.write(f"**Age:** {pf['age']} | **Risk:** {pf['risk_tolerance']}")
                    st.write(f"**Created:** {pd.to_datetime(pf['created_at']).strftime('%b %d, %Y')}")
                    if st.button("View Details", key=f"view_pf_{pf['id']}"):
                        st.session_state['view_portfolio_id'] = pf['id']
                        st.session_state['menu'] = "Dashboard"
                        st.rerun()
        else:
            st.info("No portfolios saved yet. Go to Portfolio Recommendation to create one!")

    with col2:
        st.markdown("## 📌 Watchlist Overview")
        watchlist = get_watchlist(user_id)[:5]  # Show first 5

        if watchlist:
            for ticker in watchlist:
                try:
                    data = get_stock_price(ticker)
                    price = data.get('price', 'N/A')
                    change = data.get('change', 0)
                    change_pct = data.get('changePercent', 0)

                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"**{ticker}** - {data.get('name', ticker)}")
                    with col_b:
                        color = "green" if change >= 0 else "red"
                        st.markdown(f"<span style='color:{color}'>₹{price:.2f} ({change_pct:+.2f}%)</span>",
                                    unsafe_allow_html=True)
                except Exception:
                    st.write(f"**{ticker}** - Data unavailable")
        else:
            st.info("Your watchlist is empty. Add stocks from any analysis page!")

    # Show portfolio details if selected
    if 'view_portfolio_id' in st.session_state:
        pf_id = st.session_state['view_portfolio_id']
        portfolio = get_portfolio(pf_id, user_id)
        if portfolio:
            st.markdown("---")
            st.markdown(f"## 📊 {portfolio['name']} Details")
            try:
                portfolio_data = json.loads(portfolio['portfolio_data'])
                for pf_name, details in portfolio_data.items():
                    st.markdown(f"### {pf_name}")
                    alloc_df = pd.DataFrame({
                        "Asset Class": list(details["percentages"].keys()),
                        "Allocation %": [f"{v:.2f}%" for v in details["percentages"].values()],
                        "Amount (₹)": [f"₹{v:,.2f}" for v in details["amounts"].values()],
                    })
                    st.table(alloc_df)
            except Exception as e:
                st.error(f"Error loading portfolio: {e}")

# ==================== WATCHLIST PAGE ====================
elif menu == "Watchlist":
    if not require_auth():
        st.stop()

    st.markdown('<div class="main-header">📌 My Watchlist</div>', unsafe_allow_html=True)

    user_id = get_current_user_id()
    watchlist = get_watchlist(user_id)

    if not watchlist:
        st.info("Your watchlist is empty. Add stocks from the Price, Chart, or Analysis pages!")
        st.markdown("**How to add stocks:**")
        st.markdown("1. Go to any analysis page (Price, Chart, etc.)")
        st.markdown("2. Enter a stock ticker")
        st.markdown("3. Click '➕ Add to Watchlist' button")
    else:
        st.write(f"You have **{len(watchlist)}** stocks in your watchlist:")

        # Display watchlist in a nice table
        watchlist_data = []
        for ticker in watchlist:
            try:
                data = get_stock_price(ticker)
                watchlist_data.append({
                    "Ticker": ticker,
                    "Company": data.get('name', ticker),
                    "Price": f"₹{data.get('price', 'N/A'):.2f}" if isinstance(data.get('price'), (int, float)) else "N/A",
                    "Change": f"{data.get('changePercent', 0):+.2f}%",
                    "PE Ratio": f"{data.get('peRatio', 'N/A'):.2f}" if isinstance(data.get('peRatio'), (int, float)) else "N/A"
                })
            except Exception:
                watchlist_data.append({
                    "Ticker": ticker,
                    "Company": "Data unavailable",
                    "Price": "N/A",
                    "Change": "N/A",
                    "PE Ratio": "N/A"
                })

        if watchlist_data:
            df = pd.DataFrame(watchlist_data)
            st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🔧 Manage Watchlist")

        # Remove from watchlist
        col1, col2 = st.columns(2)

        with col1:
            ticker_to_remove = st.selectbox("Select ticker to remove", watchlist)
            if st.button("🗑️ Remove from Watchlist", type="secondary"):
                if remove_from_watchlist(user_id, ticker_to_remove):
                    st.success(f"Removed {ticker_to_remove} from watchlist!")
                    st.rerun()
                else:
                    st.error("Failed to remove ticker.")

        with col2:
            if st.button("🧹 Clear Entire Watchlist", type="secondary"):
                for ticker in watchlist:
                    remove_from_watchlist(user_id, ticker)
                st.success("Watchlist cleared!")
                st.rerun()

# ==================== PRICE VIEW ====================
elif menu == "Price":
    st.subheader("📊 Stock Details")

    if st.sidebar.button("Get Stock Data"):
        data = get_stock_price(ticker)

        st.subheader("📊 Stock Details")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Company", data["name"])
        col2.metric("Price", data["price"])
        col3.metric("Market Cap", data["marketCap"])
        col4.metric("PE Ratio", data["peRatio"])

        # Add to watchlist button (if authenticated)
        if is_authenticated():
            user_id = get_current_user_id()
            if is_in_watchlist(user_id, ticker):
                st.success(f"✅ {ticker} is in your watchlist!")
            else:
                if st.button(f"➕ Add {ticker} to Watchlist"):
                    if add_to_watchlist(user_id, ticker):
                        st.success(f"Added {ticker} to your watchlist!")
                        st.rerun()
                    else:
                        st.error("Failed to add to watchlist (might already exist)")

# ==================== CHART VIEW ====================
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

        # Add to watchlist button
        if is_authenticated():
            user_id = get_current_user_id()
            if not is_in_watchlist(user_id, ticker):
                if st.button(f"➕ Add {ticker} to Watchlist"):
                    if add_to_watchlist(user_id, ticker):
                        st.success(f"Added {ticker} to your watchlist!")
                        st.rerun()
                    else:
                        st.error("Failed to add to watchlist")

# ==================== COMPARE VIEW ====================
elif menu == "Compare":
    st.subheader("📊 Compare Two Stocks")

    col1, col2 = st.columns(2)

    with col1:
        ticker1 = st.text_input("Enter First Stock", "AAPL")

    with col2:
        ticker2 = st.text_input("Enter Second Stock", "TSLA")

    if st.button("Compare Stocks"):
        data1 = get_stock_price(ticker1)
        data2 = get_stock_price(ticker2)

        st.write("## Comparison Result")

        c1, c2 = st.columns(2)

        # First Stock
        with c1:
            st.markdown(f"### {ticker1}")
            st.metric("Company", data1["name"])
            st.metric("Price", data1["price"])
            st.metric("Market Cap", data1["marketCap"])
            st.metric("PE Ratio", data1["peRatio"])
            if is_authenticated():
                user_id = get_current_user_id()
                if not is_in_watchlist(user_id, ticker1):
                    if st.button(f"➕ Add {ticker1} to Watchlist", key=f"add_{ticker1}"):
                        add_to_watchlist(user_id, ticker1)
                        st.success(f"Added {ticker1}!")
                        st.rerun()

        # Second Stock
        with c2:
            st.markdown(f"### {ticker2}")
            st.metric("Company", data2["name"])
            st.metric("Price", data2["price"])
            st.metric("Market Cap", data2["marketCap"])
            st.metric("PE Ratio", data2["peRatio"])
            if is_authenticated():
                user_id = get_current_user_id()
                if not is_in_watchlist(user_id, ticker2):
                    if st.button(f"➕ Add {ticker2} to Watchlist", key=f"add_{ticker2}"):
                        add_to_watchlist(user_id, ticker2)
                        st.success(f"Added {ticker2}!")
                        st.rerun()

    hist1 = get_stock_history(ticker1, "6mo")
    hist2 = get_stock_history(ticker2, "6mo")

    st.write("## Closing price comparison (6 months)")

    chart_data = {
        ticker1: hist1["Close"],
        ticker2: hist2["Close"]
    }

    st.line_chart(chart_data)
    st.bar_chart(chart_data)
    st.area_chart(chart_data)

# ==================== CORRELATION HEATMAP VIEW ====================
elif menu == "Correlation Heatmap":
    st.subheader("📊 Stock Correlation Heatmap")
    st.write("Analyze how different stocks move in relation to each other.")

    st.markdown("### Select Stocks")
    col1, col2 = st.columns([3, 1])

    with col1:
        tickers_input = st.text_input(
            "Enter Stock Tickers (comma-separated)",
            "AAPL,GOOGL,MSFT,AMZN",
            help="Enter at least 2 stock tickers separated by commas"
        )

    with col2:
        corr_period = st.selectbox(
            "Time Period",
            ["3mo", "6mo", "1y", "2y"],
            index=2,
            help="Period for historical data analysis"
        )

    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    if st.button("Generate Correlation Heatmap", type="primary"):
        if len(tickers) < 2:
            st.error("Please enter at least 2 stock tickers.")
        else:
            with st.spinner(f"Fetching data for {len(tickers)} stocks..."):
                corr_matrix = get_correlation_matrix(tickers, period=corr_period)

                if corr_matrix is not None and not corr_matrix.empty:
                    st.success("✅ Correlation matrix generated successfully!")

                    st.markdown("### Correlation Matrix Table")
                    st.dataframe(corr_matrix.style.format("{:.3f}"), use_container_width=True)

                    fig = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.index,
                        colorscale='RdBu',
                        zmid=0,
                        zmin=-1,
                        zmax=1,
                        text=corr_matrix.values,
                        texttemplate="%{text:.2f}",
                        textfont={"size": 10},
                        hoverongaps=False,
                        colorbar=dict(title="Correlation", tickvals=[-1, -0.5, 0, 0.5, 1])
                    ))

                    fig.update_layout(
                        title=f"Stock Returns Correlation Matrix ({corr_period} period)",
                        xaxis_title="Stock Ticker",
                        yaxis_title="Stock Ticker",
                        height=600,
                        width=800
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Add to watchlist section for authenticated users
                    if is_authenticated():
                        st.markdown("---")
                        st.markdown("### 📌 Add All to Watchlist")
                        st.write("Add all these tickers to your watchlist for easy tracking:")
                        user_id = get_current_user_id()
                        if st.button("Add All Tickers to Watchlist"):
                            added = 0
                            for t in tickers:
                                if add_to_watchlist(user_id, t):
                                    added += 1
                            st.success(f"Added {added} new tickers to your watchlist!")
                            st.rerun()

# ==================== CHATBOT VIEW ====================
elif menu == "Chatbot":
    st.subheader("💬 Ask Financial Questions")

    user_input = st.text_input("Type your question")

    if st.button("Send"):
        reply = chatbot_response(user_input)
        st.success(reply)

# ==================== ANALYSIS VIEW ====================
elif menu == "Analysis":
    st.subheader("📈 Stock Analysis")

    if st.sidebar.button("Get Analysis"):
        data = get_stock_with_change(ticker)

        st.markdown("### 📋 Stock Summary Card")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Current Price", f"${data['price']:.2f}")
        col2.metric(
            "Day Change",
            f"${data['change']:.2f}",
            f"{data['changePercent']:.2f}%"
        )

        market_cap = data["marketCap"]
        if market_cap != "N/A" and market_cap is not None:
            if market_cap >= 1_000_000_000_000:
                market_cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                market_cap_str = f"${market_cap / 1_000_000:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
        else:
            market_cap_str = "N/A"

        col3.metric("Market Cap", market_cap_str)
        col4.metric("Sector", data["sector"])

        st.markdown("---")
        st.markdown(f"### 📈 Market Trend Analysis (Last {period})")
        trend_data = get_stock_trend(ticker, period)
        st.info(f"The current market trend for {ticker} is: **{trend_data['trend']}**")
        st.write(trend_data["description"])

        st.markdown("---")
        st.markdown("### 📊 Additional Details")

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.metric("Company", data["name"])
            st.metric("PE Ratio", f"{data['peRatio']:.2f}" if isinstance(data['peRatio'], (int, float)) else "N/A")
            rec = data.get("recommendation", "N/A").replace("_", " ").title()
            if "Buy" in rec:
                rec_disp = "🟢 " + rec
            elif "Sell" in rec:
                rec_disp = "🔴 " + rec
            elif "Hold" in rec:
                rec_disp = "🟡 " + rec
            else:
                rec_disp = rec
            st.metric("AI Recommendation", rec_disp)

        with info_col2:
            beta = data.get("beta", "N/A")
            st.metric("Beta", f"{beta:.2f}" if isinstance(beta, (int, float)) else "N/A")
            st.metric("Volume", f"{data['volume']:,}" if isinstance(data['volume'], (int, float)) else "N/A")

            if beta == "N/A" or not isinstance(beta, (int, float)):
                risk_disp = "⚪ N/A"
            elif beta < 0.8:
                risk_disp = "🟢 Low Risk"
            elif 0.8 <= beta <= 1.2:
                risk_disp = "🟡 Medium Risk"
            else:
                risk_disp = "🔴 High Risk"
            st.metric("Risk Level", risk_disp)

        with info_col3:
            st.metric("Industry", data["industry"])
            st.metric("Dividend Yield", f"{data['dividendYield']:.4f}" if isinstance(data['dividendYield'], (int, float)) else "N/A")
            st.metric("EPS (Trailing)", f"{data['eps']:.2f}" if isinstance(data['eps'], (int, float)) else "N/A")

        st.markdown("---")
        st.markdown("### 💎 Valuation Check")

        v_col1, v_col2 = st.columns(2)

        current_price = data['price']
        pe_ratio = data['peRatio']
        eps = data['eps']
        target_price = data.get('targetPrice', "N/A")

        with v_col1:
            st.write("**Metric Table**")
            val_data = {
                "Metric": ["Current Price", "PE Ratio", "EPS (TTM)", "Fair Value (Target)"],
                "Value": [
                    f"${current_price:.2f}",
                    f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A",
                    f"{eps:.2f}" if isinstance(eps, (int, float)) else "N/A",
                    f"${target_price:.2f}" if isinstance(target_price, (int, float)) else "N/A"
                ]
            }
            st.table(val_data)

        with v_col2:
            st.write("**Valuation Summary**")
            if isinstance(target_price, (int, float)) and target_price > 0:
                diff = ((target_price - current_price) / current_price) * 100
                if diff > 10:
                    st.success(f"Stock appears **Undervalued (Cheap)**. Potential upside: {diff:.2f}%")
                elif diff < -10:
                    st.error(f"Stock appears **Overvalued (Expensive)**. Potential downside: {abs(diff):.2f}%")
                else:
                    st.warning(f"Stock appears **Fairly Valued**. Deviation from target: {diff:.2f}%")
            else:
                st.info("Fair value data (Analyst Target) not available for comparison.")

            if isinstance(pe_ratio, (int, float)):
                if pe_ratio > 30:
                    st.write("⚠️ High PE ratio suggests the stock might be expensive relative to earnings.")
                elif pe_ratio < 15 and pe_ratio > 0:
                    st.write("✅ Low PE ratio suggests the stock might be a bargain.")
                else:
                    st.write("ℹ️ PE ratio is in a moderate range.")

        # Add to watchlist button
        if is_authenticated():
            user_id = get_current_user_id()
            if is_in_watchlist(user_id, ticker):
                st.success(f"✅ {ticker} is in your watchlist!")
            else:
                if st.button(f"➕ Add {ticker} to Watchlist"):
                    if add_to_watchlist(user_id, ticker):
                        st.success(f"Added {ticker} to your watchlist!")
                        st.rerun()
                    else:
                        st.error("Failed to add to watchlist")

# ==================== PORTFOLIO RECOMMENDATION VIEW ====================
elif menu == "Portfolio Recommendation":
    st.subheader("🧠 AI Portfolio Recommendation Engine")
    st.write("Get personalized portfolio suggestions based on your age, risk tolerance, and investment budget.")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Your Age", min_value=18, max_value=90, value=25, help="Age helps determine risk capacity")
    with col2:
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["Low", "Medium", "High"],
            help="Low: Capital preservation, Medium: Balanced growth, High: Maximum growth"
        )
    with col3:
        budget = st.number_input(
            "Investment Budget (₹)",
            min_value=1000,
            value=50000,
            step=1000,
            help="Total amount you want to invest"
        )

    if st.button("🔮 Generate Portfolio Recommendations", type="primary"):
        recs = generate_portfolio_recommendation(age, risk_tolerance, budget)

        st.success(f"✅ Recommendations generated for budget **₹{budget:,.0f}**")
        st.markdown("---")

        # Display each portfolio
        for portfolio_name, details in recs.items():
            st.markdown(f"## {portfolio_name}")

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("Expected Annual Return", f"{details['expected_annual_return']:.2f}%")
            with m_col2:
                st.metric("Risk Level", details['risk_level'])
            with m_col3:
                st.info(details['description'])

            st.markdown("### 📊 Asset Allocation")

            p_col1, p_col2 = st.columns([1, 1])

            with p_col1:
                st.write("**Allocation Table**")
                alloc_df = pd.DataFrame({
                    "Asset Class": list(details["percentages"].keys()),
                    "Allocation %": [f"{v:.2f}%" for v in details["percentages"].values()],
                    "Amount (₹)": [f"₹{v:,.2f}" for v in details["amounts"].values()],
                })
                st.table(alloc_df)

            with p_col2:
                st.write("**Visual Allocation**")
                import plotly.graph_objects as go
                fig = go.Figure(data=[go.Pie(
                    labels=list(details["percentages"].keys()),
                    values=list(details["percentages"].values()),
                    hole=0.4,
                    textinfo='label+percent',
                    insidetextorientation='radial'
                )])
                fig.update_layout(
                    showlegend=True,
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

        # Save portfolio section (if authenticated)
        if is_authenticated():
            st.markdown("### 💾 Save This Portfolio")
            st.write("Save these recommendations to your dashboard for future reference:")

            col1, col2 = st.columns(2)
            with col1:
                portfolio_name = st.text_input("Portfolio Name", value=f"Portfolio - {risk_tolerance} - ₹{budget:,.0f}")
            with col2:
                if st.button("💾 Save Portfolio to Dashboard", type="primary"):
                    user_id = get_current_user_id()
                    portfolio_json = json.dumps(recs)
                    pf_id = save_portfolio(user_id, portfolio_name, age, risk_tolerance, budget, portfolio_json)
                    st.success(f"✅ Portfolio saved! You can access it from your Dashboard.")
                    st.rerun()
        else:
            st.info("🔒 **Login required** to save portfolios. Please log in to store your recommendations.")

        st.markdown("## 📌 Key Insights")
        risk_lower = risk_tolerance.lower()
        if risk_lower == "low":
            st.info("🔵 **Low Risk Profile**: Your portfolios emphasize capital preservation with higher debt allocation. Safe Portfolio is most suitable for you.")
        elif risk_lower == "high":
            st.success("🟢 **High Risk Profile**: Your portfolios maximize equity exposure for growth. Aggressive Portfolio aligns with your risk appetite.")
        else:
            st.warning("🟡 **Medium Risk Profile**: Balanced approach between growth and stability. Moderate Portfolio is recommended as core holding.")

        st.markdown("## 💡 Suggested Investment Products")
        st.write("Here are specific investment options for each asset class:")

        moderate_alloc = recs["Moderate Portfolio"]["amounts"]
        suggestions = get_suggested_instruments(budget, moderate_alloc)

        for asset_class, info in suggestions.items():
            if info["amount"] > 0:
                st.markdown(f"### {asset_class} (₹{info['amount']:,.2f})")
                for suggestion in info["suggestions"]:
                    st.markdown(f"- {suggestion}")

        st.markdown("---")
        st.warning("⚠️ **Disclaimer**: These are model portfolio recommendations for educational purposes. Please consult a SEBI-registered financial advisor before making any investment decisions. Past performance may not indicate future results.")

# ==================== NEWS INTELLIGENCE VIEW ====================
elif menu == "News Intelligence":
    st.subheader("📰 NLP News Intelligence Dashboard")
    st.write("Real-time news analysis with AI-powered impact scoring and trading signals")

    st.markdown("## 🔥 Top Trending Companies Today")
    st.write("Companies with the highest news volume and impact scores")

    with st.spinner("Analyzing news trends across major stocks..."):
        trending = get_trending_companies(limit=10)

    if trending:
        trending_df = pd.DataFrame(trending)
        display_df = trending_df.copy()
        display_df["Rank"] = range(1, len(display_df) + 1)
        display_df["Signal Display"] = display_df.apply(
            lambda x: f"{x['signal_emoji']} {x['overall_signal']}", axis=1
        )
        display_df["Sentiment Display"] = display_df.apply(
            lambda x: f"{'🟢' if x['overall_sentiment'] == 'Positive' else '🔴' if x['overall_sentiment'] == 'Negative' else '🟡'} {x['overall_sentiment']}", axis=1
        )

        display_columns = ["Rank", "ticker", "news_count", "positive_ratio", "negative_ratio",
                          "avg_impact_score", "Sentiment Display", "Signal Display", "trending_score"]
        column_names = {
            "ticker": "Ticker",
            "news_count": "News Count",
            "positive_ratio": "Positive %",
            "negative_ratio": "Negative %",
            "avg_impact_score": "Avg Impact",
            "trending_score": "Trend Score"
        }

        display_df_formatted = display_df[display_columns].rename(columns=column_names)
        display_df_formatted["Positive %"] = display_df_formatted["Positive %"].apply(lambda x: f"{x:.1%}")
        display_df_formatted["Negative %"] = display_df_formatted["Negative %"].apply(lambda x: f"{x:.1%}")

        st.dataframe(
            display_df_formatted.style.background_gradient(
                subset=["Trend Score", "Avg Impact"],
                cmap="YlOrRd"
            ),
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns(2)

        with col1:
            top5 = trending_df.head(5)
            fig1 = go.Figure(data=[
                go.Bar(
                    x=top5["ticker"],
                    y=top5["trending_score"],
                    marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
                    text=top5["trending_score"],
                    textposition='auto',
                )
            ])
            fig1.update_layout(
                title="Trending Score (Higher = More Trending)",
                xaxis_title="Stock Ticker",
                yaxis_title="Score",
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = go.Figure(data=[
                go.Pie(
                    labels=top5["ticker"],
                    values=top5["news_count"],
                    hole=0.4,
                    textinfo='label+percent',
                    insidetextorientation='radial'
                )
            ])
            fig2.update_layout(
                title="News Volume Share (Top 5)",
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 🏆 Top 3 Detailed Analysis")
        for idx, company in enumerate(trending[:3]):
            ticker = company["ticker"]
            with st.expander(f"#{idx+1}: {ticker} - {company['overall_signal']} (Impact: {company['avg_impact_score']}/10)"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("News Count", company["news_count"])
                c2.metric("Positive Ratio", f"{company['positive_ratio']:.1%}")
                c3.metric("Negative Ratio", f"{company['negative_ratio']:.1%}")
                c4.metric("Avg Impact", f"{company['avg_impact_score']}/10")

                recent_news = stock_news(ticker, limit=3)
                if recent_news:
                    st.markdown("**Latest News:**")
                    for article in recent_news:
                        st.markdown(f"- {article['signal_emoji']} **{article['title']}**")
                        st.caption(f"  {article['summary']} | Impact: {article['impact_score']}/10 | Signal: {article['signal']}")

    st.markdown("---")
    st.markdown("## 📡 Latest Market News with AI Signals")
    st.write("Real-time market news with impact analysis and trading signals")

    col1, col2 = st.columns([3, 1])
    with col1:
        news_limit = st.slider("Number of news articles", 5, 30, 15)
    with col2:
        if st.button("🔄 Refresh News", type="primary"):
            st.rerun()

    with st.spinner("Fetching and analyzing market news..."):
        market_news = get_market_news(limit=news_limit)

    if market_news:
        signal_counts = {"Strong Buy": 0, "Buy": 0, "Hold": 0, "Sell": 0, "Strong Sell": 0}
        for article in market_news:
            signal_counts[article["signal"]] += 1

        st.markdown("### 🎯 Signal Summary")
        sig_col1, sig_col2, sig_col3, sig_col4, sig_col5 = st.columns(5)
        with sig_col1:
            st.metric("🟢 Strong Buy", signal_counts["Strong Buy"])
        with sig_col2:
            st.metric("🟢 Buy", signal_counts["Buy"])
        with sig_col3:
            st.metric("🟡 Hold", signal_counts["Hold"])
        with sig_col4:
            st.metric("🔴 Sell", signal_counts["Sell"])
        with sig_col5:
            st.metric("🔴 Strong Sell", signal_counts["Strong Sell"])

        st.markdown("### 📋 News Feed")
        for i, article in enumerate(market_news):
            if "Strong Buy" in article["signal"] or "Buy" in article["signal"]:
                card_color = "#d4edda"
                border_color = "#28a745"
            elif "Strong Sell" in article["signal"] or "Sell" in article["signal"]:
                card_color = "#f8d7da"
                border_color = "#dc3545"
            else:
                card_color = "#fff3cd"
                border_color = "#ffc107"

            st.markdown(f"""
            <div style="
                background-color: {card_color};
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 5px solid {border_color};
            ">
                <h4 style="margin:0 0 10px 0;">{article['signal_emoji']} {article['title']}</h4>
                <p style="margin:5px 0;"><strong>Summary:</strong> {article['summary']}</p>
                <p style="margin:5px 0;"><strong>Sentiment:</strong> {article['signal_emoji']} {article['sentiment']} |
                <strong>Impact:</strong> {article['impact_score']}/10 |
                <strong>Signal:</strong> {article['signal']}</p>
                <p style="margin:5px 0; font-size:0.9em; color:#666;">
                    📅 {article['published']} | 🌐 {article['source']}
                </p>
                <a href="{article['link']}" target="_blank">🔗 Read Full Article →</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not fetch market news. Please try again later.")
