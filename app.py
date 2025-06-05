import numpy as np
import pandas as pd
import yfinance as yf
from keras.models import load_model
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Load model
model = load_model('C:/Users/Atharva/OneDrive/Desktop/stock price prediction/Stock Predictions Model.keras')

# Streamlit header
st.header('📈 Stock Market Predictor')

# Input stock symbol
stock = st.text_input('Enter Stock Symbol', 'GOOG')

# Date range
start = '2015-01-01'
end = '2025-01-01'

# Download stock data
data = yf.download(stock, start, end)

# Check if data is valid
if data.empty or 'Close' not in data.columns:
    st.error(f"⚠️ Failed to fetch stock data for '{stock}'. Please check the symbol or try again later.")
    st.stop()

# Show raw data
st.subheader('Stock Data')
st.write(data)

# Prepare training and test data
data_train = pd.DataFrame(data.Close[0:int(len(data)*0.80)])
data_test = pd.DataFrame(data.Close[int(len(data)*0.80): len(data)])

scaler = MinMaxScaler(feature_range=(0,1))

pas_100_days = data_train.tail(100)
data_test = pd.concat([pas_100_days, data_test], ignore_index=True)

# Check again before scaling
if data_test.empty:
    st.error("⚠️ Not enough data to make predictions.")
    st.stop()

data_test_scale = scaler.fit_transform(data_test)

# Price vs MA50
st.subheader('Price vs MA50')
ma_50_days = data.Close.rolling(50).mean()
fig1 = plt.figure(figsize=(8,6))
plt.plot(ma_50_days, 'r', label='MA50')
plt.plot(data.Close, 'g', label='Closing Price')
plt.legend()
st.pyplot(fig1)

# Price vs MA50 vs MA100
st.subheader('Price vs MA50 vs MA100')
ma_100_days = data.Close.rolling(100).mean()
fig2 = plt.figure(figsize=(8,6))
plt.plot(ma_50_days, 'r', label='MA50')
plt.plot(ma_100_days, 'b', label='MA100')
plt.plot(data.Close, 'g', label='Closing Price')
plt.legend()
st.pyplot(fig2)

# Price vs MA100 vs MA200
st.subheader('Price vs MA100 vs MA200')
ma_200_days = data.Close.rolling(200).mean()
fig3 = plt.figure(figsize=(8,6))
plt.plot(ma_100_days, 'r', label='MA100')
plt.plot(ma_200_days, 'b', label='MA200')
plt.plot(data.Close, 'g', label='Closing Price')
plt.legend()
st.pyplot(fig3)

# Prepare test input for prediction
x = []
y = []

for i in range(100, data_test_scale.shape[0]):
    x.append(data_test_scale[i-100:i])
    y.append(data_test_scale[i, 0])

x = np.array(x)
y = np.array(y)

# ✅ Reshape for LSTM input
x = x.reshape(x.shape[0], x.shape[1], 1)

# Make predictions
try:
    predict = model.predict(x)
    predict = predict * (1 / scaler.scale_)
    y = y * (1 / scaler.scale_)

    # Plot results
    st.subheader('Original Price vs Predicted Price')
    fig4 = plt.figure(figsize=(8,6))
    plt.plot(predict, 'r', label="Predicted Price")
    plt.plot(y, 'g', label="Original Price")
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    st.pyplot(fig4)

except Exception as e:
    st.error(f"Prediction failed ❌: {e}")
