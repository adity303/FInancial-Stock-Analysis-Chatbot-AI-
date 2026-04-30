import pandas as pd
import yfinance as yf

def generate_portfolio_recommendation(age, risk_tolerance, budget):
    """
    Generate Safe, Moderate, and Aggressive portfolio recommendations
    based on age, risk profile, and total budget with detailed asset allocation.
    """
    risk = risk_tolerance.lower()

    # Age-based risk adjustment (younger = more risk capacity)
    if age < 25:
        age_equity_boost = 10
        age_debt_reduction = 5
    elif age < 30:
        age_equity_boost = 5
        age_debt_reduction = 2
    elif age > 55:
        age_equity_boost = -10
        age_debt_reduction = -5
    elif age > 45:
        age_equity_boost = -5
        age_debt_reduction = -2
    else:
        age_equity_boost = 0
        age_debt_reduction = 0

    # Base allocations with age adjustment
    model_allocations = {
        "Safe Portfolio": {
            "Equity (Stocks/ETFs)": max(15, 25 + age_equity_boost),
            "Debt (Bonds/FDs/NPS)": min(60, 50 + age_debt_reduction),
            "Gold (Sovereign Gold Bonds/ETF)": 15,
            "Cash/Equivalents (Sweep FD/Liquid Funds)": 10,
        },
        "Moderate Portfolio": {
            "Equity (Stocks/ETFs)": max(35, 50 + age_equity_boost),
            "Debt (Bonds/FDs/NPS)": min(40, 30 + age_debt_reduction),
            "Gold (Sovereign Gold Bonds/ETF)": 10,
            "Cash/Equivalents (Sweep FD/Liquid Funds)": 10,
        },
        "Aggressive Portfolio": {
            "Equity (Stocks/ETFs)": max(50, 70 + age_equity_boost),
            "Debt (Bonds/FDs/NPS)": min(30, 15 + age_debt_reduction),
            "Gold (Sovereign Gold Bonds/ETF)": 5,
            "Cash/Equivalents (Sweep FD/Liquid Funds)": 10,
        },
    }

    # Risk tolerance fine-tuning
    if "low" in risk:
        # Shift towards safety across all portfolios
        for portfolio in model_allocations:
            model_allocations[portfolio]["Equity (Stocks/ETFs)"] = max(10, model_allocations[portfolio]["Equity (Stocks/ETFs)"] - 10)
            model_allocations[portfolio]["Debt (Bonds/FDs/NPS)"] = min(70, model_allocations[portfolio]["Debt (Bonds/FDs/NPS)"] + 10)
    elif "high" in risk:
        # Shift towards growth across all portfolios
        for portfolio in model_allocations:
            model_allocations[portfolio]["Equity (Stocks/ETFs)"] = min(90, model_allocations[portfolio]["Equity (Stocks/ETFs)"] + 10)
            model_allocations[portfolio]["Debt (Bonds/FDs/NPS)"] = max(5, model_allocations[portfolio]["Debt (Bonds/FDs/NPS)"] - 10)

    # Expected returns and risk metrics by asset class (annualized, approximate)
    return_metrics = {
        "Equity (Stocks/ETFs)": {"expected_return": 12.0, "risk_level": "High", "volatility": "High"},
        "Debt (Bonds/FDs/NPS)": {"expected_return": 7.5, "risk_level": "Low", "volatility": "Low"},
        "Gold (Sovereign Gold Bonds/ETF)": {"expected_return": 8.0, "risk_level": "Medium", "volatility": "Medium"},
        "Cash/Equivalents (Sweep FD/Liquid Funds)": {"expected_return": 4.5, "risk_level": "Very Low", "volatility": "Very Low"},
    }

    # Convert percentages to rupee allocation and calculate portfolio metrics
    recommendations = {}
    for portfolio_name, alloc in model_allocations.items():
        total_pct = sum(alloc.values())
        normalized = {k: round((v / total_pct) * 100, 2) for k, v in alloc.items()}
        rupee_split = {k: round((pct / 100) * budget, 2) for k, pct in normalized.items()}

        # Calculate weighted expected return and risk score
        weighted_return = sum(normalized[asset] / 100 * return_metrics[asset]["expected_return"] for asset in normalized)
        risk_scores = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4}
        avg_risk_score = sum(normalized[asset] / 100 * risk_scores[return_metrics[asset]["risk_level"]] for asset in normalized)

        # Determine overall risk label
        if avg_risk_score < 1.8:
            portfolio_risk = "Very Low"
        elif avg_risk_score < 2.5:
            portfolio_risk = "Low"
        elif avg_risk_score < 3.2:
            portfolio_risk = "Moderate"
        elif avg_risk_score < 3.8:
            portfolio_risk = "High"
        else:
            portfolio_risk = "Very High"

        recommendations[portfolio_name] = {
            "percentages": normalized,
            "amounts": rupee_split,
            "expected_annual_return": round(weighted_return, 2),
            "risk_level": portfolio_risk,
            "description": get_portfolio_description(portfolio_name, age, risk),
        }

    return recommendations

def get_portfolio_description(portfolio_name, age, risk):
    """Generate a description for each portfolio type."""
    descriptions = {
        "Safe Portfolio": "Focuses on capital preservation with majority in debt and gold. Suitable for conservative investors or those nearing retirement.",
        "Moderate Portfolio": "Balanced mix of equity and debt for steady growth with controlled risk. Ideal for most investors with medium-term goals.",
        "Aggressive Portfolio": "Equity-heavy allocation for maximum long-term growth. Best for young investors with high risk appetite and long investment horizon."
    }
    return descriptions[portfolio_name]

def get_suggested_instruments(budget, allocation):
    """
    Suggest specific investment products based on allocation and budget.
    Returns a dict with instrument suggestions for each asset class.
    """
    suggestions = {}

    # Equity suggestions (ETFs and Index Funds)
    if allocation.get("Equity (Stocks/ETFs)", 0) > 0:
        equity_amount = allocation["Equity (Stocks/ETFs)"]
        suggestions["Equity (Stocks/ETFs)"] = {
            "amount": equity_amount,
            "suggestions": [
                "Nifty 50 ETF (NIFTYBEES) - Low cost broad market exposure",
                "Nifty Next 50 ETF (JUNIORBEES) - Mid-cap growth potential",
                "Sectoral ETFs (BANKBEES, ITBEES) - Thematic exposure",
                "Index Funds (UTI Nifty Index, HDFC Index Fund)",
            ],
            "note": "Consider SIP for disciplined investing. Start with ETFs for lower expense ratios."
        }

    # Debt suggestions
    if allocation.get("Debt (Bonds/FDs/NPS)", 0) > 0:
        debt_amount = allocation["Debt (Bonds/FDs/NPS)"]
        suggestions["Debt (Bonds/FDs/NPS)"] = {
            "amount": debt_amount,
            "suggestions": [
                "Bank FDs (Senior citizens get higher rates)",
                "Corporate FDs (Higher returns, slightly more risk)",
                "Government Bonds (Sovereign guarantee)",
                "NPS (Tax benefits under 80CCD(1B))",
                "Debt Mutual Funds (Liquid, Ultra-short duration)",
            ],
            "note": "Diversify across tenures for liquidity. Consider tax implications."
        }

    # Gold suggestions
    if allocation.get("Gold (Sovereign Gold Bonds/ETF)", 0) > 0:
        gold_amount = allocation["Gold (Sovereign Gold Bonds/ETF)"]
        suggestions["Gold (Sovereign Gold Bonds/ETF)"] = {
            "amount": gold_amount,
            "suggestions": [
                "Sovereign Gold Bonds (SGB) - 2.5% interest + tax-free gold gains",
                "Gold ETFs (Nippon Gold ETF, HDFC Gold ETF)",
                "Digital Gold (MMTC-PAMP, SafeGold)",
            ],
            "note": "SGBs offer best value with interest and tax benefits. Limit to 10-15% of portfolio."
        }

    # Cash/Equivalents suggestions
    if allocation.get("Cash/Equivalents (Sweep FD/Liquid Funds)", 0) > 0:
        cash_amount = allocation["Cash/Equivalents (Sweep FD/Liquid Funds)"]
        suggestions["Cash/Equivalents (Sweep FD/Liquid Funds)"] = {
            "amount": cash_amount,
            "suggestions": [
                "Sweep-in FDs (Higher returns than savings account)",
                "Liquid Mutual Funds (Redemption in T+1)",
                "High-yield Savings Account",
                "Money Market Funds",
            ],
            "note": "Keep for emergency fund (3-6 months expenses) and short-term needs."
        }

    return suggestions

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