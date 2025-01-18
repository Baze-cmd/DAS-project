import pandas as pd
import ta
from datetime import datetime, timedelta


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


def get_action(key, value, data):
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
        # Compare the current price with the moving average
        current_price = data['Last_trade_price'].iloc[-1]  # Assuming data is the DataFrame
        if current_price > value:
            return 'Buy'
        elif current_price < value:
            return 'Sell'
        return 'Hold'

    return 'Hold'


def print_results(indicators , data):
    result_parts = []
    result_parts.append("Oscillators:")
    for key, value in indicators["Oscillators"].items():
        result_parts.append(f"{key}: {value} - {get_action(key, value , data)}")
    result_parts.append("\nMoving averages:")
    for key, value in indicators["Moving averages"].items():
        result_parts.append(f"{key}: {value} - {get_action(key, value, data)}")
    for part in result_parts:
        print(part)


def main():
    print("Thanks for joining us, have a nice day")
    return
    # name = 'ADIN'
    # df = get_data_for(name)

    # Apply filter by timeframe
    #df_filtered = filter_data_by_timeframe(df, 'daily')
    # df_filtered = filter_data(df, '1 year')
    #
    # indicators = calc_indicators(df_filtered)
    #
    # signals = get_signals(indicators)
    #
    # print(signals)
    #
    # print("Indicators:", indicators)
    # print("Generated Signals:", signals)


if __name__ == "__main__":
    main()

