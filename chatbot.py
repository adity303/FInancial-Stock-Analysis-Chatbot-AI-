from stock_utils import get_stock_price
from news_utils import stock_news
import matplotlib.pyplot as plt
import os

def chatbot_response(user_input):
    text = user_input.lower()

    stock_tickers = {
        "apple": "AAPL",
        "tcs": "TCS.NS",  # Assuming .NS for Indian stocks
        "infosys": "INFY.NS", # Assuming .NS for Indian stocks
        "tesla": "TSLA",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "amazon": "AMZN",
        "reliance": "RELIANCE.NS", # Assuming .NS for Indian stocks
        "tata": "TATAMOTORS.NS", # Assuming .NS for Indian stocks
        "nvidea": "NVDA",
        "facebook": "FB"
    }

    # Greetings
    if "hello" in text or "hi" in text:
        return "### Hello! 👋\nI am your **Financial Assistant**. How can I assist you with stock-related information today?"

    elif "bye" in text:
        return "### Goodbye! 👋\nFeel free to return if you have more financial queries. Have a great day!"
    
    # Stock Price and News Queries
    for company, ticker in stock_tickers.items():
        if f"{company} stock price" in text or f"price of {company}" in text:
            stock_data = get_stock_price(ticker)
            if stock_data and stock_data["price"] != "N/A":
                market_cap_billion = stock_data["marketCap"] / 1_000_000_000 if stock_data["marketCap"] != "N/A" else "N/A"
                company_name = stock_data["name"]
                current_price = stock_data["price"]
                pe_ratio = stock_data["peRatio"]
                
                return (f"### 📈 Stock Data: **{company_name}** (`{ticker}`)\n\n"
                        f"- **Current Price:** ${current_price:.2f}\n"
                        f"- **Market Cap:** ${market_cap_billion:.2f} Billion\n"
                        f"- **PE Ratio:** {pe_ratio:.2f}")
            else:
                return f"⚠️ **Could not retrieve stock price** for {company.capitalize()}. Please check the company name or try again later."
        
        elif f"{company} news" in text or f"news about {company}" in text:
            news_articles = stock_news(company)
            if news_articles:
                # Generate sentiment distribution for the pie chart
                sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
                for article in news_articles:
                    sentiment_counts[article["sentiment"]] += 1

                labels = list(sentiment_counts.keys())
                sizes = list(sentiment_counts.values())
                colors = ["#4CAF50", "#F44336", "#FFEB3B"]
                explode = [0.1 if s == max(sizes) and max(sizes) > 0 else 0 for s in sizes] # Explode the largest slice

                # Create pie chart
                fig1, ax1 = plt.subplots(figsize=(8, 8))
                ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
                        shadow=True, startangle=140, textprops={'fontsize': 14, 'color': 'black'})
                ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                ax1.set_title(f'News Sentiment Distribution for {company.capitalize()}', fontsize=16, color='navy', fontweight='bold')

                # Save the pie chart
                os.makedirs("charts", exist_ok=True)
                chart_filename = f"charts/{company}_sentiment_pie_chart.png"
                plt.savefig(chart_filename, bbox_inches='tight', pad_inches=0.5, dpi=100)
                plt.close(fig1)
                
                response = f"### 📰 Top 3 News Headlines for **{company.capitalize()}**:\n\n"
                for i, article in enumerate(news_articles[:3]):
                    article_title = article["title"]
                    article_sentiment = article["sentiment"]
                    
                    sentiment_emoji = "🟢" if article_sentiment == "Positive" else "🔴" if article_sentiment == "Negative" else "🟡"
                    
                    response += f"{i+1}. **{article_title}**\n   *Sentiment: {sentiment_emoji} {article_sentiment}*\n\n"
                    
                response += f"📊 *A sentiment distribution pie chart has been saved at:* `{chart_filename}`"
                return response
            else:
                return f"⚠️ **Could not retrieve news** for {company.capitalize()}. Please try again later."

    # Finance Terms
    if "pe ratio" in text:
        return ("### **Price-to-Earnings (P/E) Ratio** 📊\n\n"
                "The P/E Ratio is a valuation metric that compares a company's current share price to its earnings per share. "
                "A higher P/E ratio generally indicates that investors are expecting higher earnings growth in the future.")

    elif "market cap" in text:
        return ("### **Market Capitalization (Market Cap)** 🏢\n\n"
                "Market Cap represents the total market value of a company's outstanding shares. "
                "It is calculated by multiplying the current share price by the total number of outstanding shares.")

    elif "volume" in text:
        return ("### **Trading Volume** 📈\n\n"
                "Trading Volume refers to the number of shares or contracts traded in a security or an entire market during a given period. "
                "It is a key indicator of market activity and liquidity.")

    elif "rsi" in text:
        return ("### **Relative Strength Index (RSI)** 📉\n\n"
                "The RSI is a momentum oscillator that measures the speed and change of price movements. "
                "RSI values range from 0 to 100, with readings above 70 typically indicating an overbought condition and readings below 30 indicating an oversold condition.")

    else:
        return ("🤖 **I apologize**, but I can only provide information related to financial stocks and general finance terms. "
                "Please rephrase your query or ask about a specific company's stock price or news.")