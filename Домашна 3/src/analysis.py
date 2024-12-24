import pandas as pd
import ta
import os
import sqlite3
import matplotlib.pyplot as plt


def get_data_for(name):
    db_path = os.getcwd()
    db_path = os.path.abspath(os.path.join(db_path, '..'))
    db_path = os.path.abspath(os.path.join(db_path, '..'))
    db_path = os.path.join(db_path, 'Домашна 1\\src\\data\\database.sqlite')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT Date, Last_trade_price, Max, Min FROM {name}")
    column_names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(rows, columns=column_names)
    # reverse the order of the data
    df = df.iloc[::-1].reset_index(drop=True)
    return df


def RSI(df):
    indicator = ta.momentum.RSIIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.rsi().iloc[-1], 2)


def StochasticRSI(df):
    indicator = ta.momentum.StochRSIIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.stochrsi_d().iloc[-1], 2)


def CII(df):
    indicator = ta.trend.CCIIndicator(close=df['Last_trade_price'], high=df['Max'], low=df['Min'], fillna=True)
    return round(indicator.cci().iloc[-1], 2)


def awesome(df):
    indicator = ta.momentum.AwesomeOscillatorIndicator(high=df['Max'], low=df['Min'], fillna=True)
    return round(indicator.awesome_oscillator().iloc[-1], 2)


def SMA(df):
    indicator = ta.trend.SMAIndicator(close=df['Last_trade_price'], window=2, fillna=True)
    return round(indicator.sma_indicator().iloc[-1], 2)


def EMA(df):
    indicator = ta.trend.EMAIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.ema_indicator().iloc[-1], 2)


def Ichimoku(df):
    indicator = ta.trend.IchimokuIndicator(high=df['Max'], low=df['Min'], fillna=True)
    return round(indicator.ichimoku_conversion_line().iloc[-1], 2)


def Trix(df):
    indicator = ta.trend.TRIXIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.trix().iloc[-1], 2)


def KAMA(df):
    indicator = ta.momentum.KAMAIndicator(close=df['Last_trade_price'], fillna=True)
    return round(indicator.kama().iloc[-1], 2)


def WMA(df):
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

def main():
    name = 'ADIN'
    indicators = calc_indicators(get_data_for(name))
    print(indicators)


main()
