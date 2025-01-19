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


def prepare_lstm_data(df, feature_col='Last_trade_price', look_back=60):
    """
    Prepares the data for training an LSTM model by scaling the input data and
    creating sequences for the LSTM.

    :param df: DataFrame containing the stock data.
    :param feature_col: Name of the column used as the target feature.
    :param look_back: Number of time steps to use as input for predicting the next step.
    :return: Tuple (X, y, scaler), where X and y are the input and output sequences, and
             scaler is the fitted MinMaxScaler instance.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[[feature_col]])

    X, y = [], []
    # Create sequences of 'look_back' steps for the input and output
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])

    # Convert to numpy arrays and reshape for LSTM input
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    return X, y, scaler


def build_lstm_model(input_shape):
    """
    Builds and compiles an LSTM model.

    :param input_shape: Shape of the input data for the LSTM.
    :return: Compiled LSTM model.
    """
    model = Sequential()
    # Add the first LSTM layer with return_sequences=True for stacking layers
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))  # Dropout to prevent overfitting
    # Add the second LSTM layer
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    # Output layer for predicting a single value
    model.add(Dense(units=1))
    # Compile the model with Adam optimizer and mean squared error loss
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def train_lstm_model(model, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
    """
    Trains the LSTM model.

    :param model: Compiled LSTM model.
    :param X_train: Training input data.
    :param y_train: Training target data.
    :param X_val: Validation input data.
    :param y_val: Validation target data.
    :param epochs: Number of training epochs.
    :param batch_size: Batch size for training.
    :return: Training history object.
    """
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val),
                        epochs=epochs, batch_size=batch_size)
    return history


def predict_with_lstm(model, X_test, scaler):
    """
    Generates predictions using the trained LSTM model and inverses the scaling.

    :param model: Trained LSTM model.
    :param X_test: Test input data.
    :param scaler: Fitted MinMaxScaler instance used during data preparation.
    :return: Array of predictions in the original scale.
    """
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    return predictions


def evaluate_model(y_true, y_pred):
    """
    Evaluates the performance of the model using Mean Squared Error (MSE) and
    Root Mean Squared Error (RMSE).

    :param y_true: True target values.
    :param y_pred: Predicted values.
    """
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    print(f"Mean Squared Error: {mse}")
    print(f"Root Mean Squared Error: {rmse}")


def lstm_predict(df):
    """
    High-level function to predict the next stock price using an LSTM model.

    :param df: DataFrame containing stock data with at least a 'Last_trade_price' column.
    :return: Tuple (predicted price, mse) containing the next predicted price and
             the model's Mean Squared Error on the test set.
    """
    # Use only the relevant column for prediction
    df = df[['Last_trade_price']]
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df)

    # Split the data into training and testing sets (70% training, 30% testing)
    train_size = int(len(scaled_data) * 0.7)
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size:]

    # Helper function to create sequences for LSTM
    def create_sequences(data, seq_length):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)

    seq_length = 60  # Number of days to use for predicting the next day's price
    X_train, y_train = create_sequences(train_data, seq_length)
    X_test, y_test = create_sequences(test_data, seq_length)

    # Build and compile the LSTM model
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model on the training set
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)

    # Make predictions on the test set and compute MSE
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    y_test = scaler.inverse_transform(y_test.reshape(-1, 1))
    mse = mean_squared_error(y_test, predictions)

    # Predict the next price based on the most recent data
    last_sequence = scaled_data[-seq_length:]
    last_sequence = np.expand_dims(last_sequence, axis=0)
    next_price = model.predict(last_sequence)
    next_price = scaler.inverse_transform(next_price)

    return next_price[0, 0], mse
