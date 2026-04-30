import feedparser
from textblob import TextBlob
from datetime import datetime
import re

def analyze_news_impact(title, published_parsed=None):
    sentiment = TextBlob(title).sentiment.polarity
    sentiment_magnitude = abs(sentiment) * 5
    
    recency_factor = 0
    if published_parsed:
        try:
            pub_date = datetime(*published_parsed[:6])
            hours_old = (datetime.now() - pub_date).total_seconds() / 3600
            if hours_old < 1:
                recency_factor = 3.0
            elif hours_old < 6:
                recency_factor = 2.5
            elif hours_old < 24:
                recency_factor = 2.0
            elif hours_old < 72:
                recency_factor = 1.0
            else:
                recency_factor = 0.5
        except:
            recency_factor = 1.0
    
    high_impact_keywords = [
        'earnings', 'profit', 'revenue', 'acquisition', 'merger',
        'bankruptcy', 'lawsuit', 'scandal', 'ceo', 'layoff',
        'dividend', 'split', 'ipo', 'fraud', 'recall',
        'regulatory', 'approval', 'breakthrough', 'contract',
        'partnership', 'investment', 'funding', 'buyback'
    ]
    title_lower = title.lower()
    keyword_matches = sum(1 for kw in high_impact_keywords if kw in title_lower)
    keyword_bonus = min(keyword_matches * 0.5, 2.0)
    
    impact_score = min(sentiment_magnitude + recency_factor + keyword_bonus, 10.0)
    return round(impact_score, 1)

def get_trading_signal(sentiment, impact_score):
    if sentiment == "Positive":
        if impact_score >= 7.0:
            return "Strong Buy", "🟢"
        elif impact_score >= 4.0:
            return "Buy", "🟢"
        else:
            return "Hold", "🟡"
    elif sentiment == "Negative":
        if impact_score >= 7.0:
            return "Strong Sell", "🔴"
        elif impact_score >= 4.0:
            return "Sell", "🔴"
        else:
            return "Hold", "🟡"
    else:
        return "Hold", "🟡"

def generate_headline_summary(title, max_words=15):
    words = title.split()
    if len(words) <= max_words:
        return title
    return ' '.join(words[:max_words]) + "..."

def stock_news(company, limit=10):
    url = f"https://news.google.com/rss/search?q={company}+stock+finance"
    feed = feedparser.parse(url)
    news_list = []

    for entry in feed.entries[:limit]:
        title = entry.title
        sentiment_polarity = TextBlob(title).sentiment.polarity

        if sentiment_polarity > 0.1:
            mood = "Positive"
            mood_color = "green"
        elif sentiment_polarity < -0.1:
            mood = "Negative"
            mood_color = "red"
        else:
            mood = "Neutral"
            mood_color = "orange"

        published = entry.get("published", "")
        published_str = "N/A"
        published_parsed = None
        if published:
            try:
                published_dt = datetime(*entry.published_parsed[:6])
                published_str = published_dt.strftime("%b %d, %Y %I:%M %p")
                published_parsed = entry.published_parsed
            except:
                published_str = published

        source = "Unknown"
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title_clean = parts[0]
            source = parts[1] if len(parts) > 1 else "Unknown"
        else:
            title_clean = title

        summary = generate_headline_summary(title_clean, max_words=12)
        impact_score = analyze_news_impact(title_clean, published_parsed)
        signal, signal_emoji = get_trading_signal(mood, impact_score)

        news_list.append({
            "title": title_clean,
            "summary": summary,
            "link": entry.link,
            "source": source,
            "published": published_str,
            "sentiment": mood,
            "sentiment_color": mood_color,
            "impact_score": impact_score,
            "signal": signal,
            "signal_emoji": signal_emoji
        })

    return news_list

def get_market_news(limit=10):
    url = "https://news.google.com/rss/search?q=stock+market+finance+ investing"
    feed = feedparser.parse(url)
    news_list = []

    for entry in feed.entries[:limit]:
        title = entry.title
        sentiment_polarity = TextBlob(title).sentiment.polarity

        if sentiment_polarity > 0.1:
            mood = "Positive"
            mood_color = "green"
        elif sentiment_polarity < -0.1:
            mood = "Negative"
            mood_color = "red"
        else:
            mood = "Neutral"
            mood_color = "orange"

        published = entry.get("published", "")
        published_str = "N/A"
        published_parsed = None
        if published:
            try:
                published_dt = datetime(*entry.published_parsed[:6])
                published_str = published_dt.strftime("%b %d, %Y %I:%M %p")
                published_parsed = entry.published_parsed
            except:
                published_str = published

        source = "Unknown"
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title_clean = parts[0]
            source = parts[1] if len(parts) > 1 else "Unknown"
        else:
            title_clean = title

        summary = generate_headline_summary(title_clean, max_words=12)
        impact_score = analyze_news_impact(title_clean, published_parsed)
        signal, signal_emoji = get_trading_signal(mood, impact_score)

        news_list.append({
            "title": title_clean,
            "summary": summary,
            "link": entry.link,
            "source": source,
            "published": published_str,
            "sentiment": mood,
            "sentiment_color": mood_color,
            "impact_score": impact_score,
            "signal": signal,
            "signal_emoji": signal_emoji
        })

    return news_list

def get_trending_companies(tickers=None, limit=5):
    if tickers is None:
        tickers = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "META", "NVDA", "NFLX", "AMD", "INTC"
        ]
    
    trending_scores = []
    
    for ticker in tickers:
        try:
            news = stock_news(ticker, limit=5)
            
            if not news:
                continue
            
            total_news = len(news)
            positive_count = sum(1 for n in news if n["sentiment"] == "Positive")
            negative_count = sum(1 for n in news if n["sentiment"] == "Negative")
            
            avg_impact = sum(n["impact_score"] for n in news) / total_news
            
            recent_news = [n for n in news if "hour" in n["published"].lower() or "minute" in n["published"].lower()]
            recency_ratio = len(recent_news) / total_news if total_news > 0 else 0
            
            sentiment_strength = (positive_count - negative_count) / total_news if total_news > 0 else 0
            trending_score = (total_news * 0.3) + (avg_impact * 0.4) + (recency_ratio * 0.3) + (sentiment_strength * 2)
            
            if positive_count > negative_count:
                overall_sentiment = "Positive"
            elif negative_count > positive_count:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"
            
            overall_signal, signal_emoji = get_trading_signal(overall_sentiment, avg_impact)
            
            trending_scores.append({
                "ticker": ticker,
                "company_name": ticker,
                "news_count": total_news,
                "positive_ratio": positive_count / total_news if total_news > 0 else 0,
                "negative_ratio": negative_count / total_news if total_news > 0 else 0,
                "avg_impact_score": round(avg_impact, 1),
                "overall_sentiment": overall_sentiment,
                "overall_signal": overall_signal,
                "signal_emoji": signal_emoji,
                "trending_score": round(trending_score, 2)
            })
        except Exception as e:
            continue
    
    trending_scores.sort(key=lambda x: x["trending_score"], reverse=True)
    return trending_scores[:limit]

def get_market_news(limit=10):
    """
    Fetches general market/financial news.
    """
    url = "https://news.google.com/rss/search?q=stock+market+finance+ investing"
    feed = feedparser.parse(url)

    news_list = []

    for entry in feed.entries[:limit]:
        title = entry.title
        sentiment = TextBlob(title).sentiment.polarity  # type: ignore[attr-defined]

        if sentiment > 0.1:
            mood = "Positive"
            mood_color = "green"
        elif sentiment < -0.1:
            mood = "Negative"
            mood_color = "red"
        else:
            mood = "Neutral"
            mood_color = "orange"

        published = entry.get("published", "")
        if published:
            try:
                published_dt = datetime(*entry.published_parsed[:6])
                published_str = published_dt.strftime("%b %d, %Y %I:%M %p")
            except:
                published_str = published
        else:
            published_str = "N/A"

        source = "Unknown"
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title_clean = parts[0]
            source = parts[1] if len(parts) > 1 else "Unknown"
        else:
            title_clean = title

        news_list.append({
            "title": title_clean,
            "link": entry.link,
            "source": source,
            "published": published_str,
            "sentiment": mood,
            "sentiment_color": mood_color
        })

    return news_list