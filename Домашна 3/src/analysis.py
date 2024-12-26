import pandas as pd
import ta
import os
import sqlite3


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
def filter_data_by_timeframe(df, timeframe):
    if timeframe == 'daily':
        return df
    elif timeframe == 'weekly':
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)  # Set 'Date' as the index for resampling
        return df.resample('W').mean().reset_index()  # Resample weekly
    elif timeframe == 'monthly':
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)  # Set 'Date' as the index for resampling
        return df.resample('M').mean().reset_index()  # Resample monthly
    else:
        raise ValueError("Invalid timeframe. Use 'daily', 'weekly', or 'monthly'.")


# Add generate_signals function here
def generate_signals(oscillators, moving_averages):
    signals = []
    # logic for Buy/Sell based on RSI
    rsi = oscillators['Relative Strength Index']
    stochastic_rsi = oscillators['Stochastic RSI %D']

    if rsi is not None:
        if rsi < 30 and stochastic_rsi < 0.2:
            signals.append('Buy')
        elif rsi > 70 and stochastic_rsi > 0.8:
            signals.append('Sell')
        else:
            signals.append('Hold')

    return signals


def main():
    name = 'ADIN'
    df = get_data_for(name)

    # Apply filter by timeframe
    df_filtered = filter_data_by_timeframe(df, 'daily')  # monthly/weekly

    indicators = calc_indicators(df_filtered)
    signals = generate_signals(indicators['Oscillators'], indicators['Moving averages'])

    print("Indicators:", indicators)
    print("Generated Signals:", signals)


if __name__ == "__main__":
    main()


