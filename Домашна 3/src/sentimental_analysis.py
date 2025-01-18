# TODO: Transfer all the logic for the sentimental analysis here
from newspaper import Article
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import requests


def get_stock_news(stock_name):
    api_key = "157a774cc5d648588081e2a151e3d112"
    url = f"https://newsapi.org/v2/everything?q={stock_name}&apiKey={api_key}"

    response = requests.get(url)
    data = response.json()

    if data.get('status') == 'ok':
        return data['articles']  # Correctly accessing articles from NewsAPI response
    else:
        print(f"Error fetching news for {stock_name}: {data.get('message')}")
        return []


def analyze_sentiment_vader(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score['compound']


def analyze_sentiment_textblob(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity


def analyze_news_for_stock(stock_name):
    articles = get_stock_news(stock_name)
    positive_sentiment_count = 0
    negative_sentiment_count = 0

    for article in articles:
        try:
            article_url = article['url']
            article_data = Article(article_url)
            article_data.download()
            article_data.parse()

            # Use both VADER and TextBlob for sentiment analysis
            vader_score = analyze_sentiment_vader(article_data.text)
            textblob_score = analyze_sentiment_textblob(article_data.text)

            # VADER sentiment analysis
            if vader_score > 0:
                positive_sentiment_count += 7
            elif vader_score < 0:
                negative_sentiment_count += 7

            # TextBlob sentiment analysis (optional to use both scores)
            if textblob_score > 0:
                positive_sentiment_count += 3
            elif textblob_score < 0:
                negative_sentiment_count += 3

        except Exception as e:
            pass

    if positive_sentiment_count > negative_sentiment_count:
        return "Buy"
    else:
        return "Sell"
