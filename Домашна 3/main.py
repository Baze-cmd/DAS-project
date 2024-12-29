from src import technical_analysis, sentimental_analysis , LSTM_analysis
import os
import sqlite3
import pandas as pd
import ta




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


def get_table_names(limit=None):
    db_path = os.getcwd()
    db_path = os.path.join(db_path, 'database.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT name FROM sqlite_master WHERE type='table'"
    if limit is not None:
        query += f" LIMIT {limit}"
    try:
        cursor.execute(query)
        table_names = cursor.fetchall()
    finally:
        cursor.close()
    return [table[0] for table in table_names]





def do_analysis(stock_name):
    print(f"Processing data for {stock_name}:")

    # Get technical indicators for the stock
    df = get_data_for(stock_name)
    df_filtered = technical_analysis.filter_data(df, '1 year')
    indicators = technical_analysis.calc_indicators(df_filtered)
    technical_analysis.print_results(indicators)

    # Perform sentiment analysis
    sentiment_action = sentimental_analysis.analyze_news_for_stock(stock_name)
    print(f"Sentiment Analysis for {stock_name}: {sentiment_action}")

    # LSTM price prediction
    LSTM_analysis.lstm_result(df,stock_name)


def main():
    stock_name = input("Enter the stock name (or leave blank for all stocks): ").strip()

    if stock_name == "":
        names = get_table_names()
        for stock in names:
            stock_name = stock
            do_analysis(stock_name)
    else:
        do_analysis(stock_name)


if __name__ == "__main__":
    main()
