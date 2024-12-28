import pandas as pd
import ta
import os
import sqlite3
import datetime
from datetime import datetime, timedelta
import requests
from newspaper import Article
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import requests





def get_data_for(name):
    db_path = os.getcwd()
    db_path = os.path.join(db_path, 'database.sqlite')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT Date, Last_trade_price, Max, Min FROM {name}")
    column_names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(rows, columns=column_names)
    # reverse the order of the data
    df = df.iloc[::-1].reset_index(drop=True)
    # Convert the 'Date' column to datetime type
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)  # day-first format
    return df


def RSI(df):
    if len(df) < 14:
        return None
    indicator = ta.momentum.RSIIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.rsi().iloc[-1], 2)


def StochasticRSI(df):
    if len(df) < 14:
        return None
    indicator = ta.momentum.StochRSIIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.stochrsi_d().iloc[-1], 2)


def CII(df):
    if len(df) < 20:
        return None
    indicator = ta.trend.CCIIndicator(close=df['Last_trade_price'], high=df['Max'], low=df['Min'], fillna=True)
    return round(indicator.cci().iloc[-1], 2)


def awesome(df):
    if len(df) < 34:
        return None
    indicator = ta.momentum.AwesomeOscillatorIndicator(high=df['Max'], low=df['Min'], fillna=True)
    return round(indicator.awesome_oscillator().iloc[-1], 2)


def SMA(df):
    if len(df) < 4:
        return None
    indicator = ta.trend.SMAIndicator(close=df['Last_trade_price'], window=2, fillna=True)
    return round(indicator.sma_indicator().iloc[-1], 2)


def EMA(df):
    if len(df) < 14:
        return None
    indicator = ta.trend.EMAIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.ema_indicator().iloc[-1], 2)


def Ichimoku(df):
    if len(df) < 52:
        return None
    indicator = ta.trend.IchimokuIndicator(high=df['Max'], low=df['Min'], fillna=True)
    return round(indicator.ichimoku_conversion_line().iloc[-1], 2)


def Trix(df):
    if len(df) < 15:
        return None
    indicator = ta.trend.TRIXIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.trix().iloc[-1], 2)


def KAMA(df):
    if len(df) < 40:
        return None
    indicator = ta.momentum.KAMAIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.kama().iloc[-1], 2)


def WMA(df):
    if len(df) < 9:
        return None
    indicator = ta.trend.WMAIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.wma().iloc[-1], 2)


def calc_indicators(data):
    oscillators = {}
    moving_averages = {}
    oscillators['Relative Strength Index'] = RSI(data)
    oscillators['Stochastic RSI %D'] = StochasticRSI(data)
    oscillators['Commodity Channel Index'] = CII(data)
    oscillators['Trix'] = Trix(data)
    oscillators['Awesome Oscillator'] = awesome(data)
    moving_averages['Simple Moving Average'] = SMA(data)
    moving_averages['Exponential Moving Average'] = EMA(data)
    moving_averages['Ichimoku'] = Ichimoku(data)
    moving_averages['Kaufman’s Adaptive Moving Average'] = KAMA(data)
    moving_averages['Weighted Moving Average'] = WMA(data)
    return {'Oscillators': oscillators, 'Moving averages': moving_averages}


# Add filter_data_by_timeframe function here
# def filter_data_by_timeframe(df, timeframe):
#     if timeframe == 'daily':
#         return df
#     elif timeframe == 'weekly':
#         df['Date'] = pd.to_datetime(df['Date'])
#         df.set_index('Date', inplace=True)  # Set 'Date' as the index for resampling
#         return df.resample('W').mean().reset_index()  # Resample weekly
#     elif timeframe == 'monthly':
#         df['Date'] = pd.to_datetime(df['Date'])
#         df.set_index('Date', inplace=True)  # Set 'Date' as the index for resampling
#         return df.resample('M').mean().reset_index()  # Resample monthly
#     else:
#         raise ValueError("Invalid timeframe. Use 'daily', 'weekly', or 'monthly'.")


def filter_data(df, timePeriod):
    possible_time_periods = ['All time', '5 years', '1 year', '1 month', '1 week', '1 day']
    if timePeriod not in possible_time_periods or timePeriod == 'All time':
        return df

    df = df.copy()
    df = df.iloc[::-1].reset_index(drop=True)
    original_date_format = '%d.%m.%Y'
    df['Date'] = pd.to_datetime(df['Date'], format=original_date_format)
    now = datetime.now()
    cutoff_mapping = {'5 years': timedelta(days=5 * 365), '1 year': timedelta(days=365), '1 month': timedelta(days=30), '1 week': timedelta(weeks=1), '1 day': timedelta(days=1)}
    date_cutoff = now - cutoff_mapping[timePeriod]
    filtered_df = df[df['Date'] >= date_cutoff].copy()
    filtered_df['Date'] = filtered_df['Date'].dt.strftime(original_date_format)
    return filtered_df


# Add generate_signals function here
# def generate_signals(df, moving_averages):
#     signals = []
#     # logic for Buy/Sell based on RSI
#     rsi = df['Relative Strength Index']
#     stochastic_rsi = df['Stochastic RSI %D']
#
#     if rsi is not None:
#         if rsi < 30 and stochastic_rsi < 0.2:
#             signals.append('Buy')
#         elif rsi > 70 and stochastic_rsi > 0.8:
#             signals.append('Sell')
#         else:
#             signals.append('Hold')
#
#     return signals

def get_action(key, value):
    if value is None:
        return 'Hold'

    if key == 'Relative Strength Index':
        if value > 70:
            return 'Sell'
        elif value < 30:
            return 'Buy'
        return 'Hold'

    elif key == 'Stochastic RSI %D':
        if value > 80:
            return 'Sell'
        elif value < 20:
            return 'Buy'
        return 'Hold'

    elif key == 'Commodity Channel Index':
        if value > 100:
            return 'Sell'
        elif value < -100:
            return 'Buy'
        return 'Hold'

    elif key == 'Trix':
        if value > 0:
            return 'Buy'
        elif value < 0:
            return 'Sell'
        return 'Hold'

    elif key == 'Awesome Oscillator':
        if value > 0:
            return 'Buy'
        elif value < 0:
            return 'Sell'
        return 'Hold'

    elif key in ['Simple Moving Average', 'Exponential Moving Average',
                       'Kaufman’s Adaptive Moving Average', 'Weighted Moving Average',
                       'Ichimoku']:
        return 'Hold'

    return 'Hold'


def get_stock_news(stock_name):
    api_key = "Insert_API_KEY_HERE"
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
                positive_sentiment_count += 1
            elif vader_score < 0:
                negative_sentiment_count += 1

            # TextBlob sentiment analysis (optional to use both scores)
            if textblob_score > 0:
                positive_sentiment_count += 1
            elif textblob_score < 0:
                negative_sentiment_count += 1

        except Exception as e:
            pass

    if positive_sentiment_count > negative_sentiment_count:
        return "Buy"
    else:
        return "Sell"


def main():
    stock_name = input("Enter the stock name (or leave blank for all stocks): ").strip()

    if stock_name == "":
        # If no stock is entered, process all stock tables from the database
        db_path = os.getcwd()
        db_path = os.path.join(db_path, 'database.sqlite')

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        stock_tables = cursor.fetchall()
        conn.close()

        for stock in stock_tables:
            stock_name = stock[0]
            print(f"\nProcessing data for {stock_name}:")

            # Get technical indicators for the stock
            df = get_data_for(stock_name)
            df_filtered = filter_data(df, '1 year')
            indicators = calc_indicators(df_filtered)
            signals = {}

            for key, value in indicators["Oscillators"].items():
                signals[key] = get_action(key, value)

            for key, value in indicators["Moving averages"].items():
                signals[key] = get_action(key, value)

            # Perform sentiment analysis
            sentiment_action = analyze_news_for_stock(stock_name)
            print(f"Sentiment Analysis for {stock_name}: {sentiment_action}")

            # Combine sentiment with technical analysis
            if sentiment_action == "Buy":
                print(f"Overall recommendation for {stock_name}: Buy (Sentiment + Technical Analysis)")
            else:
                print(f"Overall recommendation for {stock_name}: Sell (Sentiment + Technical Analysis)")

            print("Generated Signals for ", stock_name)
            print(signals)
            print("Indicators:", indicators)

    else:
        # If a stock name is entered, process only that stock
        df = get_data_for(stock_name)
        df_filtered = filter_data(df, '1 year')
        indicators = calc_indicators(df_filtered)
        signals = {}

        for key, value in indicators["Oscillators"].items():
            signals[key] = get_action(key, value)

        for key, value in indicators["Moving averages"].items():
            signals[key] = get_action(key, value)

        # Perform sentiment analysis
        sentiment_action = analyze_news_for_stock(stock_name)
        print(f"Sentiment Analysis for {stock_name}: {sentiment_action}")

        # Combine sentiment with technical analysis
        if sentiment_action == "Buy":
            print(f"Overall recommendation for {stock_name}: Buy (Sentiment + Technical Analysis)")
        else:
            print(f"Overall recommendation for {stock_name}: Sell (Sentiment + Technical Analysis)")

        print(f"\nGenerated Signals for {stock_name}:")
        print(signals)
        print("Indicators:", indicators)


if __name__ == "__main__":
    main()




