import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
import ta
from datetime import datetime, timedelta
import numpy as np





def prepare_lstm_data(df, feature_col='Last_trade_price', look_back=60):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[[feature_col]])

    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    return X, y, scaler


def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def train_lstm_model(model, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=batch_size)
    return history


def predict_with_lstm(model, X_test, scaler):
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    return predictions


def evaluate_model(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    print(f"Mean Squared Error: {mse}")
    print(f"Root Mean Squared Error: {rmse}")


def lstm_predict(df):
    # Prepare the data
    df = df[['Last_trade_price']]
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df)

    # Define the training and validation split
    train_size = int(len(scaled_data) * 0.7)
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size:]

    # Create sequences for LSTM
    def create_sequences(data, seq_length):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)

    seq_length = 60  # Use the last 60 days to predict the next day
    X_train, y_train = create_sequences(train_data, seq_length)
    X_test, y_test = create_sequences(test_data, seq_length)

    # Build the LSTM model
    model = Sequential([LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)), Dropout(0.2), LSTM(50, return_sequences=False), Dropout(0.2), Dense(1)])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)

    # Evaluate the model
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    y_test = scaler.inverse_transform(y_test.reshape(-1, 1))
    mse = mean_squared_error(y_test, predictions)

    # Predict the next price
    last_sequence = scaled_data[-seq_length:]
    last_sequence = np.expand_dims(last_sequence, axis=0)
    next_price = model.predict(last_sequence)
    next_price = scaler.inverse_transform(next_price)

    return next_price[0, 0], mse


def lstm_result(df):
    try:
        lstm_prediction, mse = lstm_predict(df,stock_name)
        print(f"LSTM Predicted Price for {stock_name}: {lstm_prediction:.2f}")
        print(f"LSTM Model MSE: {mse:.4f}")
    except Exception as e:
        print(f"LSTM prediction failed for {stock_name}: {e}")
        lstm_prediction = None

    # Combine sentiment with technical analysis
    if sentiment_action == "Buy" and (lstm_prediction is None or lstm_prediction > df_filtered['Last_trade_price'].iloc[-1]):
        print(f"Overall recommendation for {stock_name}: Buy (Sentiment + Technical Analysis + LSTM)")
    else:
        print(f"Overall recommendation for {stock_name}: Sell (Sentiment + Technical Analysis + LSTM)")