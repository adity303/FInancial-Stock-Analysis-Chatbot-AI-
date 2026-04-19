import feedparser
from textblob import TextBlob

def stock_news(company):
    # Constructs a Google News RSS feed URL for the company’s stock.
    url = f"https://news.google.com/rss/search?q={company}+stock"
    feed = feedparser.parse(url)
    
    news_list = [] # Initializes an empty list to store processed news items.
    
    for entry in feed.entries[:5]: # Iterates through the first 5 news articles
        title = entry.title # Extracts the title of the news article
        
        # TextBlob(title) - analyzes the headline text.
        sentiment = TextBlob(title).sentiment.polarity  # Analyzes the sentiment of the title using TextBlob
        
        # Applying conditions for sentiment analysis (Classifying the mood)
        if sentiment > 0:
            mood = "Positive"
        elif sentiment < 0:
            mood = "Negative"
        else:
            mood = "Neutral"
         
        # Appending to the list    
        news_list.append({
            "title": title,
            "link": entry.link,
            "sentiment": mood
        })
        
    return news_list