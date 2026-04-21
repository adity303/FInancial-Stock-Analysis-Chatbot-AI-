import yfinance as yf

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
        "open": info.get("open", "N/A")
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
        "beta": info.get("beta", "N/A"),
        "dividendYield": info.get("dividendYield", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A")
    }