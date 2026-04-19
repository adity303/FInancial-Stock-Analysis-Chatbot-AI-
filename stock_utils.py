import yfinance as yf

# Function to get current stock price
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "name": info.get("longName", "N/A"),
        "price": info.get("currentPrice", "N/A"),
        "marketCap": info.get("marketCap", "N/A"),
        "peRatio": info.get("trailingPE", "N/A")
    }

# Function to get historical stock data
def get_stock_history(ticker, period="6mo"): # for 6 months 
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist