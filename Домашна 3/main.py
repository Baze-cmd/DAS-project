import os
import sqlite3
import pandas as pd
from typing import List, Optional
from src import technical_analysis, sentimental_analysis, LSTM_analysis


class StockDataProcessor:
    """
    Handles data retrieval and analysis for stock data stored in the SQLite database.
    """

    def __init__(self, db_name: str = "database.sqlite"):
        self.db_path = os.path.join(os.getcwd(), db_name)

    def get_data_for(self, name: str) -> pd.DataFrame:
        """
        Retrieves data for a specific stock.

        :param name: The name of the stock (table name in the database).
        :return: DataFrame containing the stock data.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT Date, Last_trade_price, Max, Min FROM {name}")
            column_names = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
        finally:
            conn.close()

        df = pd.DataFrame(rows, columns=column_names)
        df = df.iloc[::-1].reset_index(drop=True)  # Reverse order of the data
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)  # Convert 'Date' to datetime
        return df

    def get_table_names(self, limit: Optional[int] = None) -> List[str]:
        """
        Retrieves the list of table names from the database.

        :param limit: Optional limit on the number of table names to retrieve.
        :return: List of table names.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            if limit is not None:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            table_names = cursor.fetchall()
        finally:
            conn.close()

        return [table[0] for table in table_names]


class StockAnalyzer:
    """
    Handles analysis operations for a given stock, including technical analysis, sentiment analysis, and LSTM predictions.
    """

    def __init__(self, processor: StockDataProcessor):
        self.processor = processor

    def do_analysis(self, stock_name: str):
        """
        Perform analysis for a given stock.

        :param stock_name: Name of the stock to analyze.
        """
        print(f"Processing data for {stock_name}:")

        # Get technical indicators for the stock
        df = self.processor.get_data_for(stock_name)
        df_filtered = technical_analysis.filter_data(df, '1 year')
        indicators = technical_analysis.calc_indicators(df_filtered)
        technical_analysis.print_results(indicators, df_filtered)

        # Perform sentiment analysis
        sentiment_action = sentimental_analysis.analyze_news_for_stock(stock_name)
        print(f"Sentiment Analysis for {stock_name}: {sentiment_action}")

        # LSTM price prediction
        try:
            lstm_prediction, mse = LSTM_analysis.lstm_predict(df)
            print(f"LSTM Predicted Price for {stock_name}: {lstm_prediction:.2f}")
            print(f"LSTM Model MSE: {mse:.4f}")
        except Exception as e:
            print(f"LSTM prediction failed for {stock_name}: {e}")
            lstm_prediction = None

        # Combine sentiment with technical analysis
        if sentiment_action == "Buy" and (
                lstm_prediction is None or lstm_prediction > df_filtered['Last_trade_price'].iloc[-1]):
            print(f"Overall recommendation for {stock_name}: Buy (Sentiment + Technical Analysis + LSTM)")
        else:
            print(f"Overall recommendation for {stock_name}: Sell (Sentiment + Technical Analysis + LSTM)")


if __name__ == "__main__":
    processor = StockDataProcessor()
    analyzer = StockAnalyzer(processor)

    stock_name = input("Enter the stock name (or leave blank for all stocks): ").strip()

    if stock_name == "":
        table_names = processor.get_table_names()
        for name in table_names:
            analyzer.do_analysis(name)
    else:
        analyzer.do_analysis(stock_name)
