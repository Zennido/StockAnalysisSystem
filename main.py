import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import datetime

# Set the theme of the app
st.set_page_config(page_title="Stock Price Comparison", page_icon="📈", layout="wide")

# Apply dark theme with blue accents using Streamlit's CSS injection
st.markdown("""
    <style>
    body {
        background-color: #0f0f0f;
        color: white;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
    }
    .stSelectbox>div>div>div {
        background-color: #1f77b4;
        color: white;
    }
    .stDownloadButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
    }
    .stTextInput>div>div {
        background-color: #2a2a2a;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Predefined list of popular stocks
STOCK_OPTIONS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA']

# Cache stock data to avoid multiple API calls
@st.cache_data
def fetch_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

# Predict stock price based on linear regression model
def predict_stock_price(df):
    df_copy = df[['Close']].copy()
    df_copy['date'] = (df_copy.index - df_copy.index.min()).days
    
    model = LinearRegression()
    model.fit(df_copy[['date']], df_copy[['Close']])
    
    next_day = [[df_copy['date'].max() + 1]]
    prediction = model.predict(next_day)
    
    return prediction[0][0]

# Visualization function to compare multiple stocks
# Visualization function to compare multiple stocks using line graphs
def visualize_data(stock_data, selected_symbols):
    plt.figure(figsize=(10, 6))
    
    # Dark theme: set the background to black and other dark theme settings
    plt.style.use('dark_background')
    
    for symbol in selected_symbols:
        df = stock_data[symbol]

        # Plot the closing prices as solid lines
        plt.plot(df.index, df['Close'], label=f'{symbol} Close Price', color='#1f77b4', linewidth=2)

        # Plot the 50-day moving average as dashed lines
        plt.plot(df.index, df['MA50'], label=f'{symbol} 50-day MA', color='#ff7f0e', linestyle='--', linewidth=2)

    # Set the title, axis labels, and legend
    plt.title('Stock Price Comparison (Line Graph)', color='white', fontsize=16)
    plt.xlabel('Date', color='white', fontsize=12)
    plt.ylabel('Price (USD)', color='white', fontsize=12)
    
    # Customize the tick colors and grid
    plt.xticks(color='white')
    plt.yticks(color='white')
    plt.grid(True, color='gray')

    # Add the legend
    plt.legend(loc='upper left', fontsize=10)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Display the plot in Streamlit
    st.pyplot(plt)


# Function to handle stock fetching and predictions
def fetch_and_predict(symbols, start_date, end_date):
    stock_data = {}
    predictions = {}
    
    for symbol in symbols:
        df = fetch_stock_data(symbol, start_date, end_date)
        if not df.empty:
            df['MA50'] = df['Close'].rolling(window=50).mean()  # Calculate 50-day moving average
            stock_data[symbol] = df
            predictions[symbol] = predict_stock_price(df)
    
    return stock_data, predictions

# Sidebar input options
st.sidebar.header('Stock Comparison Settings')

# Date range inputs with default values
end_date = st.sidebar.date_input("Select end date:", datetime.date.today())
start_date = st.sidebar.date_input("Select start date:", end_date - datetime.timedelta(days=180))

# Stock symbol selection using multiselect
selected_symbols = st.sidebar.multiselect("Select stocks to compare:", STOCK_OPTIONS, default=['AAPL', 'MSFT'])

# Run button to trigger fetching and predictions
if st.sidebar.button("Fetch Data and Predict"):
    # Fetch stock data and make predictions
    stock_data, predictions = fetch_and_predict(selected_symbols, start_date, end_date)
    
    if stock_data:
        # Display predicted prices
        st.header("Predicted Stock Prices for the Next Day")
        for symbol, prediction in predictions.items():
            st.subheader(f"{symbol}: ${prediction:.2f}")
        
        # Visualize the stock prices with technical indicators
        st.header("Stock Price Comparison with 50-day Moving Average")
        visualize_data(stock_data, selected_symbols)
        
        # Offer download of stock data
        for symbol, df in stock_data.items():
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label=f"Download {symbol} stock data as CSV",
                data=csv,
                file_name=f'{symbol}_data.csv',
                mime='text/csv'
            )
    else:
        st.error("Failed to fetch stock data. Please try again.")

# Display instructions for first-time users
st.sidebar.info("""
- Select stocks from the dropdown.
- Adjust the date range for stock comparison.
- Click "Fetch Data and Predict" to view the stock prices and predictions.
""")
