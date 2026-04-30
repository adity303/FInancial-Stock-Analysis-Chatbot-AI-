import yfinance as yf
import pandas as pd
import numpy as np
import pandas as pd
import numpy as np

# Function to get current stock price
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "name": info.get("longName", "N/A"),
        "price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
        "marketCap": info.get("marketCap", "N/A"),
        "peRatio": info.get("trailingPE", "N/A"),
        "dayHigh": info.get("dayHigh", "N/A"),
        "dayLow": info.get("dayLow", "N/A"),
        "volume": info.get("volume", "N/A"),
        "avgVolume": info.get("averageVolume", "N/A"),
        "beta": info.get("beta", "N/A"),
        "dividendYield": info.get("dividendYield", "N/A"),
        "52WeekHigh": info.get("fiftyTwoWeekHigh", "N/A"),
        "52WeekLow": info.get("fiftyTwoWeekLow", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "previousClose": info.get("previousClose", "N/A"),
        "open": info.get("open", "N/A"),
        "recommendation": info.get("recommendationKey", "N/A")
    }

# Function to get historical stock data
def get_stock_history(ticker, period="6mo"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

# Function to get stock info with change percentage
def get_stock_with_change(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    current = info.get("currentPrice", info.get("regularMarketPrice", 0))
    previous = info.get("previousClose", 0)

    if previous and previous != 0:
        change_pct = ((current - previous) / previous) * 100
        change_abs = current - previous
    else:
        change_pct = 0
        change_abs = 0

    return {
        "name": info.get("longName", "N/A"),
        "price": current,
        "change": change_abs,
        "changePercent": change_pct,
        "volume": info.get("volume", "N/A"),
        "marketCap": info.get("marketCap", "N/A"),
        "peRatio": info.get("trailingPE", "N/A"),
        "eps": info.get("trailingEps", "N/A"),
        "beta": info.get("beta", "N/A"),
        "dividendYield": info.get("dividendYield", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "recommendation": info.get("recommendationKey", "N/A"),
        "targetPrice": info.get("targetMeanPrice", "N/A")
    }

# Helper to convert period code to human-readable label
def _get_period_label(period):
    mapping = {
        "1mo": "1 month",
        "3mo": "3 months",
        "6mo": "6 months",
        "1y": "1 year",
        "2y": "2 years"
    }
    return mapping.get(period, period)


# Function to get stock trend
def get_stock_trend(ticker, period="1mo"):
    hist = get_stock_history(ticker, period)
    if hist.empty:
        return {
            "trend": "N/A",
            "description": "Could not retrieve historical data for trend analysis."
        }

    # Calculate percentage change over the period
    start_price = hist["Close"].iloc[0]
    end_price = hist["Close"].iloc[-1]

    if start_price == 0:
        return {
            "trend": "N/A",
            "description": "Starting price is zero, cannot determine trend accurately."
        }

    change_percent = ((end_price - start_price) / start_price) * 100
    period_label = _get_period_label(period)

    trend_type = ""
    description = ""

    if change_percent > 5:  # Arbitrary threshold for bullish
        trend_type = "📈 Bullish Trend"
        description = (
            f"The stock price has shown a significant upward movement, increasing by "
            f"{change_percent:.2f}% over the last {period_label}. The price went from "
            f"${start_price:.2f} to ${end_price:.2f}. This indicates a strong positive market sentiment."
        )
    elif change_percent < -5:  # Arbitrary threshold for bearish
        trend_type = "📉 Bearish Trend"
        description = (
            f"The stock price has experienced a significant downward movement, decreasing by "
            f"{-change_percent:.2f}% over the last {period_label}. The price went from "
            f"${start_price:.2f} to ${end_price:.2f}. This suggests a negative market sentiment."
        )
    else:
        trend_type = "➖ Sideways Consolidation"
        description = (
            f"The stock price has remained relatively stable, with a change of "
            f"{change_percent:.2f}% over the last {period_label}. The price went from "
            f"${start_price:.2f} to ${end_price:.2f}. This indicates a period of consolidation "
            f"where supply and demand are relatively balanced."
        )
    
    return {
        "trend": trend_type,
        "description": description,
        "change_percent": change_percent,
        "start_price": start_price,
        "end_price": end_price,
        "period": period
    }

# Function to calculate correlation matrix for multiple stocks
def get_correlation_matrix(tickers, period="1y"):
    """
    Calculate correlation matrix for a list of stock tickers based on daily returns.
    
    Args:
        tickers: List of stock ticker symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])
        period: Time period for historical data ('1mo', '3mo', '6mo', '1y', '2y')
    
    Returns:
        DataFrame containing correlation matrix, or None if failed
    """
    if not tickers or len(tickers) < 2:
        return None
    
    # Fetch historical data for all tickers
    hist_data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if not hist.empty:
                hist_data[ticker] = hist["Close"]
        except Exception as e:
            print(f"Could not fetch data for {ticker}: {e}")
            continue
    
    if len(hist_data) < 2:
        return None
    
    # Combine into a single DataFrame
    combined_df = pd.DataFrame(hist_data)
    
    # Calculate daily returns
    returns_df = combined_df.pct_change().dropna()
    
    # Calculate correlation matrix
    correlation_matrix = returns_df.corr()
    
    return correlation_matrix
