import streamlit as st
import plotly.graph_objects as go
from stock_utils import get_stock_price, get_stock_history
from chatbot import chatbot_response
from auth import register_user, login_user

# Page Config - Streamlit
st.set_page_config(
    page_title="Stock AI Chat Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme and Professional Dashboard
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --bg-primary: #0e1117;
        --bg-secondary: #1a1d24;
        --bg-card: #262930;
        --text-primary: #fafafa;
        --text-secondary: #b0b3b8;
        --accent-blue: #3b82f6;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-purple: #8b5cf6;
        --border-color: #2d3139;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary);
    }

    /* Sidebar Radio Buttons */
    .stRadio > label {
        color: var(--text-secondary) !important;
        font-weight: 500;
    }

    .stRadio div[role="radiogroup"] > div {
        background-color: transparent !important;
        padding: 0.5rem 0;
    }

    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] {
        background-color: var(--bg-card) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        border: 1px solid var(--border-color) !important;
        transition: all 0.2s ease !important;
    }

    .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:hover {
        background-color: #363b47 !important;
        border-color: var(--accent-blue) !important;
    }

    .stRadio div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] {
        background: linear-gradient(135deg, var(--accent-blue) 0%, #2563eb 100%) !important;
        border-color: var(--accent-blue) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] span {
        color: var(--text-primary) !important;
        font-size: 1rem;
    }

    /* Sidebar Text Inputs */
    .stTextInput > div > div > input {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
    }

    .stTextInput > label {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
        font-weight: 500;
    }

    /* Sidebar Selectbox */
    .stSelectbox > div > div > select {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-blue) 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Metrics/Cards */
    [data-testid="stMetric"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }

    [data-testid="stMetric"] > div:first-child {
        color: var(--text-secondary) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetric"] > div:nth-child(2) {
        color: var(--text-primary) !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* Subheaders */
    .stSubheader {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
    }

    /* Markdown text */
    .stMarkdown p {
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
    }

    /* Success/Info/Error boxes */
    .stAlert {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }

    /* Chatbot styling */
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
    }

    .user-message {
        background: linear-gradient(135deg, #1e3a5f 0%, #1a2f4a 100%);
        border-left: 4px solid var(--accent-blue);
    }

    .bot-message {
        background: linear-gradient(135deg, #1f2937 0%, #1a1d24 100%);
        border-left: 4px solid var(--accent-green);
    }

    /* Card container */
    .card-container {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Dashboard header */
    .dashboard-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    /* Price change indicators */
    .positive-change {
        color: var(--accent-green) !important;
        font-weight: 600;
    }

    .negative-change {
        color: var(--accent-red) !important;
        font-weight: 600;
    }

    /* Ticker input section */
    .ticker-section {
        background-color: var(--bg-card);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }

    /* Chart container */
    .chart-container {
        background-color: var(--bg-card);
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }

    /* Comparison cards */
    .comparison-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, #1f2937 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 0.5rem 0;
    }

    /* Login form styling */
    .login-form {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    /* Welcome message */
    .welcome-badge {
        background: linear-gradient(135deg, var(--accent-green) 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE --------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ==================== LOGIN/SIGNUP PAGE ====================
if not st.session_state.logged_in:
    # Custom login header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>📈 Financial Stock Assistant</h1>
        <p style='color: #b0b3b8; font-size: 1.1rem;'>Your AI-Powered Trading Companion</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        menu = st.sidebar.selectbox(
            "Menu",
            ["🔐 Login", "📝 Signup"],
            label_visibility="collapsed"
        )

        if menu == "🔐 Login":
            st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Welcome Back</h2>", unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="Enter your username (max 12 characters)")
            password = st.text_input("Password", type="password", placeholder="Enter your password (4-6 characters)")

            if st.button("🔑 Login", use_container_width=True):
                success, message = login_user(username, password)

                if success:
                    st.success("✅ Login Successful! Redirecting...")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

        elif menu == "📝 Signup":
            st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Create Account</h2>", unsafe_allow_html=True)
            st.info("💡 Username: max 12 characters | Password: 4-6 characters")

            new_user = st.text_input("Username", placeholder="Choose a username")
            new_pass = st.text_input("Password", type="password", placeholder="Create a password")

            if st.button("✨ Signup", use_container_width=True):
                success, message = register_user(new_user, new_pass)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")

# ==================== DASHBOARD (LOGGED IN) ====================
else:
    # Professional Header
    st.markdown(f"""
    <div class='dashboard-header'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h1 style='margin: 0; font-size: 2rem;'>📈 Financial Dashboard</h1>
                <p style='color: #b0b3b8; margin: 0.25rem 0 0;'>AI-Powered Stock Analysis & Insights</p>
            </div>
            <div class='welcome-badge'>
                👋 Welcome, {st.session_state.username}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("---")

        # Navigation with Icons
        st.markdown("### 🧭 Navigation")
        menu = st.radio(
            "Choose View",
            ["💰 Price", "📊 Chart", "🔍 Compare", "💬 Chatbot"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Ticker Input Section
        st.markdown("### 📈 Stock Settings")
        ticker = st.text_input(
            "Stock Ticker",
            "AAPL",
            help="Enter stock symbol (e.g., AAPL, TSLA, GOOGL)"
        )

        period = st.selectbox(
            "Time Period",
            ["1mo", "3mo", "6mo", "1y", "2y"],
            help="Select historical data period"
        )

        st.markdown("---")

        # Quick Actions
        st.markdown("### ⚡ Quick Actions")

        if st.button("📋 View Portfolio", use_container_width=True):
            st.switch_page("portfolio.py") if False else st.info("Portfolio feature coming soon!")

        st.markdown("---")

        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # =============== PRICE VIEW ===============
    if menu == "💰 Price":
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>📊 Stock Details</h2>", unsafe_allow_html=True)

        if st.sidebar.button("🔍 Get Stock Data", use_container_width=True):
            data = get_stock_price(ticker)

            # Company Info Card
            st.markdown(f"""
            <div class='card-container'>
                <h3 style='margin-top: 0;'>{data['name']}</h3>
                <p style='color: #b0b3b8; margin: 0;'>Ticker: <strong>{ticker.upper()}</strong></p>
            </div>
            """, unsafe_allow_html=True)

            # Metrics in grid
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label="💰 Current Price",
                    value=f"${data['price']}" if data['price'] != "N/A" else "N/A",
                    delta=None
                )

            with col2:
                market_cap = data['marketCap']
                if market_cap != "N/A":
                    market_cap_billion = market_cap / 1_000_000_000
                    st.metric(label="🏢 Market Cap", value=f"${market_cap_billion:.2f}B")
                else:
                    st.metric(label="🏢 Market Cap", value="N/A")

            with col3:
                st.metric(
                    label="📊 P/E Ratio",
                    value=f"{data['peRatio']:.2f}" if data['peRatio'] != "N/A" else "N/A"
                )

            with col4:
                st.metric(
                    label="📈 Volume",
                    value=f"{data['volume']:,}" if data['volume'] != "N/A" else "N/A"
                )

            # Additional Details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div class='card-container'>
                    <h4 style='color: #3b82f6; margin-bottom: 1rem;'>📋 Day's Range</h4>
                    <p>High: <strong>${:.2f}</strong></p>
                    <p>Low: <strong>${:.2f}</strong></p>
                    <p>Open: <strong>${:.2f}</strong></p>
                    <p>Prev Close: <strong>${:.2f}</strong></p>
                </div>
                """.format(
                    data.get('dayHigh', 0) or 0,
                    data.get('dayLow', 0) or 0,
                    data.get('open', 0) or 0,
                    data.get('previousClose', 0) or 0
                ), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class='card-container'>
                    <h4 style='color: #10b981; margin-bottom: 1rem;'>🏭 Company Info</h4>
                    <p>Sector: <strong>{}</strong></p>
                    <p>Industry: <strong>{}</strong></p>
                    <p>Beta: <strong>{:.2f}</strong></p>
                    <p>52W High: <strong>${:.2f}</strong></p>
                    <p>52W Low: <strong>${:.2f}</strong></p>
                </div>
                """.format(
                    data.get('sector', 'N/A'),
                    data.get('industry', 'N/A'),
                    data.get('beta', 0) or 0,
                    data.get('52WeekHigh', 0) or 0,
                    data.get('52WeekLow', 0) or 0
                ), unsafe_allow_html=True)

    # =============== CHART VIEW ===============
    elif menu == "📊 Chart":
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>📈 Price Charts</h2>", unsafe_allow_html=True)

        if st.sidebar.button("📉 Show Chart", use_container_width=True):
            hist = get_stock_history(ticker, period)

            # Line Chart
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("#### 📈 Price Trend")
            st.line_chart(hist["Close"], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Volume Chart
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("#### 📊 Trading Volume")
            st.bar_chart(hist["Volume"], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Candlestick Chart with Plotly (Dark Theme)
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("#### 🕯️ Candlestick Chart")

            fig = go.Figure(data=[
                go.Candlestick(
                    x=hist.index,
                    open=hist["Open"],
                    high=hist["High"],
                    low=hist["Low"],
                    close=hist["Close"],
                    increasing_line_color='#10b981',
                    decreasing_line_color='#ef4444'
                )
            ])

            fig.update_layout(
                template="plotly_dark",
                title=f"{ticker.upper()} - {period} Candlestick",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#fafafa'),
                xaxis=dict(gridcolor='#2d3139'),
                yaxis=dict(gridcolor='#2d3139')
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =============== COMPARE VIEW ===============
    elif menu == "🔍 Compare":
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>🔍 Compare Stocks</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            ticker1 = st.text_input("First Stock Ticker", "AAPL", key="ticker1")

        with col2:
            ticker2 = st.text_input("Second Stock Ticker", "TSLA", key="ticker2")

        if st.button("📊 Compare Now", use_container_width=True):
            data1 = get_stock_price(ticker1)
            data2 = get_stock_price(ticker2)

            st.markdown("### Comparison Results")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div class='comparison-card'>
                    <h3 style='color: #3b82f6; margin-top: 0;'>{ticker1.upper()}</h3>
                    <h4>{data1['name']}</h4>
                    <hr style='border-color: #2d3139; margin: 1rem 0;'>
                </div>
                """, unsafe_allow_html=True)

                st.metric("💰 Price", f"${data1['price']}" if data1['price'] != "N/A" else "N/A")
                st.metric("🏢 Market Cap", f"${data1['marketCap']/1e9:.2f}B" if data1['marketCap'] != "N/A" else "N/A")
                st.metric("📊 P/E Ratio", f"{data1['peRatio']:.2f}" if data1['peRatio'] != "N/A" else "N/A")
                st.metric("📈 Volume", f"{data1['volume']:,}" if data1['volume'] != "N/A" else "N/A")

            with col2:
                st.markdown(f"""
                <div class='comparison-card'>
                    <h3 style='color: #8b5cf6; margin-top: 0;'>{ticker2.upper()}</h3>
                    <h4>{data2['name']}</h4>
                    <hr style='border-color: #2d3139; margin: 1rem 0;'>
                </div>
                """, unsafe_allow_html=True)

                st.metric("💰 Price", f"${data2['price']}" if data2['price'] != "N/A" else "N/A")
                st.metric("🏢 Market Cap", f"${data2['marketCap']/1e9:.2f}B" if data2['marketCap'] != "N/A" else "N/A")
                st.metric("📊 P/E Ratio", f"{data2['peRatio']:.2f}" if data2['peRatio'] != "N/A" else "N/A")
                st.metric("📈 Volume", f"{data2['volume']:,}" if data2['volume'] != "N/A" else "N/A")

            # Comparison Chart
            st.markdown("---")
            st.markdown("#### 📈 Performance Comparison (6 months)")

            hist1 = get_stock_history(ticker1, "6mo")
            hist2 = get_stock_history(ticker2, "6mo")

            chart_data = {
                ticker1: hist1["Close"],
                ticker2: hist2["Close"]
            }

            st.line_chart(chart_data, use_container_width=True)

    # =============== CHATBOT VIEW ===============
    elif menu == "💬 Chatbot":
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>💬 AI Financial Assistant</h2>", unsafe_allow_html=True)

        # Chat container
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class='chat-message user-message'>
                    <strong>👤 You:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-message bot-message'>
                    <strong>🤖 Assistant:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)

        # User input
        user_input = st.text_input(
            "Ask me anything about stocks...",
            placeholder="e.g., What is Apple's stock price? Tell me about Tesla news..."
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Send Message", use_container_width=True):
                if user_input.strip():
                    # Add user message
                    st.session_state.chat_history.append({"role": "user", "content": user_input})

                    # Get bot response
                    reply = chatbot_response(user_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})

                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a question")

        st.markdown("</div>", unsafe_allow_html=True)

        # Quick prompts
        st.markdown("#### 💡 Quick Questions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📈 Apple stock price"):
                st.session_state.chat_history.append({"role": "user", "content": "What is Apple stock price?"})
                reply = chatbot_response("What is Apple stock price?")
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

        with col2:
            if st.button("📰 Tesla news"):
                st.session_state.chat_history.append({"role": "user", "content": "Tell me Tesla news"})
                reply = chatbot_response("Tell me Tesla news")
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()