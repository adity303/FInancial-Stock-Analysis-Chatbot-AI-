import pandas as pd
import yfinance as yf

def calculate_portfolio(portfolio_list):
    """
    Enhanced portfolio calculation with comprehensive metrics.
    """
    df = pd.DataFrame(portfolio_list)

    if df.empty:
        return df

    # Calculating values
    df["Invested Amount"] = df["Quantity"] * df["Buy Price"]
    df["Current Value"] = df["Quantity"] * df["Current Price"]
    df["Profit/Loss"] = df["Current Value"] - df["Invested Amount"]
    df["Return %"] = (df["Profit/Loss"] / df["Invested Amount"]) * 100
    df["Day Change"] = 0  # Will be populated if we fetch live data
    df["Day Change %"] = 0

    return df

def get_portfolio_with_details(portfolio_list):
    """
    Returns portfolio with additional stock details like sector, beta, day change.
    """
    detailed_portfolio = []

    for item in portfolio_list:
        ticker = item["Ticker"]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            current_price = info.get("currentPrice", info.get("regularMarketPrice", item["Current Price"]))
            previous_close = info.get("previousClose", current_price)

            # Calculate day change
            day_change = current_price - previous_close if previous_close else 0
            day_change_pct = (day_change / previous_close * 100) if previous_close else 0

            detailed_portfolio.append({
                "Ticker": ticker,
                "Quantity": item["Quantity"],
                "Buy Price": item["Buy Price"],
                "Current Price": current_price,
                "Day Change": round(day_change, 2),
                "Day Change %": round(day_change_pct, 2),
                "Invested Amount": item["Quantity"] * item["Buy Price"],
                "Current Value": item["Quantity"] * current_price,
                "Profit/Loss": (item["Quantity"] * current_price) - (item["Quantity"] * item["Buy Price"]),
                "Return %": round(((current_price - item["Buy Price"]) / item["Buy Price"] * 100), 2) if item["Buy Price"] else 0,
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Beta": info.get("beta", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "PE Ratio": info.get("trailingPE", "N/A"),
                "Dividend Yield": info.get("dividendYield", "N/A")
            })
        except Exception as e:
            # Fallback to basic info if fetch fails
            detailed_portfolio.append({
                "Ticker": ticker,
                "Quantity": item["Quantity"],
                "Buy Price": item["Buy Price"],
                "Current Price": item["Current Price"],
                "Day Change": 0,
                "Day Change %": 0,
                "Invested Amount": item["Quantity"] * item["Buy Price"],
                "Current Value": item["Quantity"] * item["Current Price"],
                "Profit/Loss": (item["Quantity"] * item["Current Price"]) - (item["Quantity"] * item["Buy Price"]),
                "Return %": round(((item["Current Price"] - item["Buy Price"]) / item["Buy Price"] * 100), 2) if item["Buy Price"] else 0,
                "Sector": "N/A",
                "Industry": "N/A",
                "Beta": "N/A",
                "Market Cap": "N/A",
                "PE Ratio": "N/A",
                "Dividend Yield": "N/A"
            })

    return pd.DataFrame(detailed_portfolio)

def get_sector_allocation(portfolio_df):
    """
    Calculate portfolio allocation by sector.
    """
    if portfolio_df.empty:
        return pd.DataFrame()

    sector_data = portfolio_df.groupby("Sector").agg({
        "Current Value": "sum",
        "Invested Amount": "sum",
        "Profit/Loss": "sum"
    }).reset_index()

    sector_data["Allocation %"] = (sector_data["Current Value"] / sector_data["Current Value"].sum() * 100).round(2)
    sector_data["Sector Return %"] = ((sector_data["Current Value"] - sector_data["Invested Amount"]) / sector_data["Invested Amount"] * 100).round(2)

    return sector_data.sort_values("Current Value", ascending=False)

def get_industry_allocation(portfolio_df):
    """
    Calculate portfolio allocation by industry.
    """
    if portfolio_df.empty:
        return pd.DataFrame()

    industry_data = portfolio_df.groupby("Industry").agg({
        "Current Value": "sum",
        "Invested Amount": "sum",
        "Profit/Loss": "sum"
    }).reset_index()

    industry_data["Allocation %"] = (industry_data["Current Value"] / industry_data["Current Value"].sum() * 100).round(2)
    return industry_data.sort_values("Current Value", ascending=False)

def get_portfolio_historical_value(portfolio_list, period="6mo"):
    """
    Calculate historical portfolio value over time.
    """
    if not portfolio_list:
        return pd.DataFrame()

    # Get all unique tickers
    tickers = [item["Ticker"] for item in portfolio_list]
    quantities = {item["Ticker"]: item["Quantity"] for item in portfolio_list}

    # Fetch historical data for all tickers
    hist_data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if not hist.empty:
                hist_data[ticker] = hist["Close"]
        except:
            pass

    if not hist_data:
        return pd.DataFrame()

    # Combine into a single DataFrame
    combined = pd.DataFrame(hist_data)

    # Calculate portfolio value for each day
    portfolio_value = pd.DataFrame(index=combined.index)
    portfolio_value["Portfolio Value"] = 0

    for ticker, qty in quantities.items():
        if ticker in combined.columns:
            portfolio_value["Portfolio Value"] += combined[ticker] * qty

    return portfolio_value

def get_portfolio_stats(portfolio_df):
    """
    Calculate advanced portfolio statistics.
    """
    if portfolio_df.empty:
        return {}

    total_invested = portfolio_df["Invested Amount"].sum()
    total_current = portfolio_df["Current Value"].sum()
    total_pl = portfolio_df["Profit/Loss"].sum()

    stats = {
        "total_invested": round(total_invested, 2),
        "total_current": round(total_current, 2),
        "total_pl": round(total_pl, 2),
        "total_return_pct": round((total_pl / total_invested * 100) if total_invested else 0, 2),
        "num_positions": len(portfolio_df),
        "num_winning": len(portfolio_df[portfolio_df["Profit/Loss"] > 0]),
        "num_losing": len(portfolio_df[portfolio_df["Profit/Loss"] < 0]),
        "best_performer": portfolio_df.loc[portfolio_df["Return %"].idxmax()]["Ticker"] if not portfolio_df.empty else "N/A",
        "worst_performer": portfolio_df.loc[portfolio_df["Return %"].idxmin()]["Ticker"] if not portfolio_df.empty else "N/A",
        "max_gain_pct": round(portfolio_df["Return %"].max(), 2) if not portfolio_df.empty else 0,
        "max_loss_pct": round(portfolio_df["Return %"].min(), 2) if not portfolio_df.empty else 0
    }

    return stats 