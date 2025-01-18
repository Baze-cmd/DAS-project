from newspaper import Article
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import requests
from typing import Protocol

# Strategy interface
class SentimentAnalysisStrategy(Protocol):
    def analyze(self, text: str) -> float:
        ...

# Concrete strategies
class VaderStrategy:
    def analyze(self, text: str) -> float:
        analyzer = SentimentIntensityAnalyzer()
        sentiment_score = analyzer.polarity_scores(text)
        return sentiment_score['compound']

class TextBlobStrategy:
    def analyze(self, text: str) -> float:
        blob = TextBlob(text)
        return blob.sentiment.polarity

# Context class
class SentimentAnalyzer:
    def __init__(self, strategy: SentimentAnalysisStrategy):
        self.strategy = strategy

    def analyze(self, text: str) -> float:
        return self.strategy.analyze(text)

# Fetch stock news
def get_stock_news(stock_name: str):
    api_key = "APY_KEY_HERE"
    url = f"https://newsapi.org/v2/everything?q={stock_name}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data['articles'] if data.get('status') == 'ok' else []

# Perform sentiment analysis on news articles
def analyze_news_for_stock(stock_name: str) -> str:
    articles = get_stock_news(stock_name)
    positive_count = 0
    negative_count = 0

    vader_analyzer = SentimentAnalyzer(VaderStrategy())
    textblob_analyzer = SentimentAnalyzer(TextBlobStrategy())

    for article in articles:
        try:
            article_url = article['url']
            article_data = Article(article_url)
            article_data.download()
            article_data.parse()
            text = article_data.text

            # Use both strategies
            vader_score = vader_analyzer.analyze(text)
            textblob_score = textblob_analyzer.analyze(text)

            # Aggregate results
            if vader_score > 0:
                positive_count += 7
            elif vader_score < 0:
                negative_count += 7

            if textblob_score > 0:
                positive_count += 3
            elif textblob_score < 0:
                negative_count += 3

        except Exception:
            continue

    return "Buy" if positive_count > negative_count else "Sell"
