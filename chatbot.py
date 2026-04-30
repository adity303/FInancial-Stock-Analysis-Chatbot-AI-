from stock_utils import get_stock_price
from news_utils import stock_news
import matplotlib.pyplot as plt
import os
import re
from portfolio_utils import generate_portfolio_recommendation

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
                recommendation = stock_data.get("recommendation", "N/A").replace("_", " ").title()
                beta = stock_data.get("beta", "N/A")

                # AI Recommendation Logic
                if "Buy" in recommendation:
                    rec_emoji = "🟢 Buy"
                elif "Sell" in recommendation:
                    rec_emoji = "🔴 Sell"
                elif "Hold" in recommendation:
                    rec_emoji = "🟡 Hold"
                else:
                    rec_emoji = "⚪ N/A"

                # Risk Level Logic based on Beta (Volatility)
                if beta == "N/A":
                    risk_level = "⚪ N/A"
                elif beta < 0.8:
                    risk_level = "🟢 Low Risk"
                elif 0.8 <= beta <= 1.2:
                    risk_level = "🟡 Medium Risk"
                else:
                    risk_level = "🔴 High Risk"

                # News Sentiment for the stock
                news_articles = stock_news(company)
                news_sentiment_str = "⚪ N/A"
                if news_articles:
                    pos_count = sum(1 for a in news_articles if a["sentiment"] == "Positive")
                    neg_count = sum(1 for a in news_articles if a["sentiment"] == "Negative")
                    
                    if pos_count > neg_count:
                        news_sentiment_str = "🟢 Positive"
                    elif neg_count > pos_count:
                        news_sentiment_str = "🔴 Negative"
                    else:
                        news_sentiment_str = "🟡 Neutral"

                return (f"### 📈 Stock Data: **{company_name}** (`{ticker}`)\n\n"
                        f"- **Current Price:** ${current_price:.2f}\n"
                        f"- **Market Cap:** ${market_cap_billion:.2f} Billion\n"
                        f"- **News Sentiment:** {news_sentiment_str}")
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
                
                response = f"### 📰 NLP News Intelligence: **{company.capitalize()}**\n\n"
                response += f"#### 📊 Overall Sentiment Breakdown\n"
                for sentiment, count in sentiment_counts.items():
                    emoji = "🟢" if sentiment == "Positive" else "🔴" if sentiment == "Negative" else "🟡"
                    response += f"{emoji} **{sentiment}**: {count} articles\n"
                
                response += f"\n#### 📈 Top 5 News Articles with AI Analysis\n\n"
                for i, article in enumerate(news_articles[:5]):
                    response += f"**{i+1}. {article['title']}**\n"
                    response += f"   📝 *Summary:* {article['summary']}\n"
                    response += f"   📅 *Published:* {article['published']} | 🌐 *Source:* {article['source']}\n"
                    response += f"   😊 *Sentiment:* {article['signal_emoji']} {article['sentiment']} "
                    response += f"| 💥 *Impact Score:* **{article['impact_score']}/10**\n"
                    response += f"   🎯 *Trading Signal:* **{article['signal_emoji']} {article['signal']}**\n"
                    response += f"   🔗 [Read More]({article['link']})\n\n"
                
                response += f"📊 *Sentiment distribution chart saved at:* `{chart_filename}`\n\n"
                response += f"---\n"
                response += f"**💡 How to interpret:**\n"
                response += f"- **Impact Score (0-10):** Higher = more significant news (earnings, M&A, scandals)\n"
                response += f"- **Trading Signal:** AI-generated suggestion based on sentiment + impact\n"
                response += f"- **Strong Buy/Sell:** High-impact news with clear directional sentiment"
                
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

    # Portfolio Recommendation Query
    elif "portfolio" in text or "recommend" in text or "suggest" in text or "allocation" in text:
        # Try to extract budget, age, and risk tolerance from the query
        # Budget extraction (₹ or Rs or INR or numbers)
        budget_patterns = [
            r'₹\s*([\d,]+)',
            r'Rs\.?\s*([\d,]+)',
            r'INR\s*([\d,]+)',
            r'budget\s*[:\s]*([\d,]+)',
            r'([\d,]+)\s*(?:rupees|rs|inr)',
            r'with\s+([\d,]+)',
            r'for\s+([\d,]+)',
            r'([\d,]+)\s*(?:budget|investment|amount)'
        ]
        
        budget = 50000  # default
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                budget_str = match.group(1).replace(',', '')
                budget = float(budget_str)
                break
        
        # Age extraction
        age_match = re.search(r'age\s*[:\s]*(\d+)', text, re.IGNORECASE)
        if not age_match:
            age_match = re.search(r'(\d+)\s*(?:years?|yrs?|old)', text, re.IGNORECASE)
        age = int(age_match.group(1)) if age_match else 25  # default age
        
        # Risk tolerance extraction
        risk = "Medium"  # default
        if "safe" in text or "low risk" in text or "conservative" in text or "safest" in text:
            risk = "Low"
        elif "aggressive" in text or "high risk" in text or "risky" in text or "aggressive" in text:
            risk = "High"
        elif "moderate" in text or "medium" in text or "balanced" in text or "middle" in text:
            risk = "Medium"
        
        # Generate recommendations
        try:
            recs = generate_portfolio_recommendation(age, risk, budget)
            
            response = f"### 🧠 AI Portfolio Recommendations\n\n"
            response += f"**Your Profile:** Age {age}, {risk} Risk Tolerance, Budget ₹{budget:,.0f}\n\n"
            response += f"Here are three model portfolios tailored for you:\n\n"
            
            for portfolio_name, details in recs.items():
                response += f"#### {portfolio_name}\n"
                response += f"**Expected Return:** {details['expected_annual_return']:.2f}% annually | "
                response += f"**Risk Level:** {details['risk_level']}\n\n"
                response += f"| Asset Class | Allocation % | Amount (₹) |\n"
                response += f"|-------------|-------------|------------|\n"
                for asset, pct in details["percentages"].items():
                    amt = details["amounts"][asset]
                    response += f"| {asset} | {pct:.2f}% | ₹{amt:,.2f} |\n"
                response += f"\n*{details['description']}*\n\n"
            
            response += "---\n"
            response += "**📌 Quick Insights:**\n"
            if risk == "Low":
                response += "- **Safe Portfolio** is ideal for you - emphasizes capital preservation with higher debt allocation\n"
                response += "- **Moderate Portfolio** offers some growth while keeping risk low\n"
                response += "- Consider starting with Safe/Moderate and gradually increasing equity as you gain confidence\n"
            elif risk == "High":
                response += "- **Aggressive Portfolio** maximizes equity for long-term wealth creation\n"
                response += "- **Moderate Portfolio** still offers good growth with some downside protection\n"
                response += "- Ensure you have emergency fund before investing heavily in equity\n"
            else:
                response += "- **Moderate Portfolio** is the sweet spot - balanced growth with controlled risk\n"
                response += "- **Safe Portfolio** for stability, **Aggressive** for long-term goals\n"
                response += "- 55% equity in Moderate aligns with classic 60/40 investment strategy\n"
            
            response += "\n**💡 Suggested Products:**\n"
            response += "- **Equity:** Nifty 50 ETFs (NIFTYBEES), Index Funds, Large-cap stocks\n"
            response += "- **Debt:** Bank FDs, Corporate FDs, Debt Mutual Funds, NPS\n"
            response += "- **Gold:** Sovereign Gold Bonds (SGB), Gold ETFs\n"
            response += "- **Cash:** Liquid Funds, Sweep-in FDs\n"
            
            response += "\n⚠️ *Disclaimer: These are model allocations for educational purposes. Consult a SEBI-registered financial advisor before investing.*"
            return response
        except Exception as e:
            return f"⚠️ **Error generating portfolio:** {str(e)}\n\nPlease try again with different parameters."

    else:
        return ("🤖 **I apologize**, but I can only provide information related to financial stocks and general finance terms. "
                "Please rephrase your query or ask about a specific company's stock price or news.")