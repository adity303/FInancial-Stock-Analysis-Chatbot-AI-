import feedparser
from textblob import TextBlob
from datetime import datetime

def stock_news(company, limit=10):
    """
    Fetches financial news for a company from Google News RSS.
    Returns list of news items with sentiment analysis.
    """
    url = f"https://news.google.com/rss/search?q={company}+stock+finance"
    feed = feedparser.parse(url)

    news_list = []

    for entry in feed.entries[:limit]:
        title = entry.title

        # Sentiment analysis using TextBlob
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

        # Parse published date
        published = entry.get("published", "")
        if published:
            try:
                published_dt = datetime(*entry.published_parsed[:6])
                published_str = published_dt.strftime("%b %d, %Y %I:%M %p")
            except:
                published_str = published
        else:
            published_str = "N/A"

        # Extract source from title (Google News format: "Title - Source")
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