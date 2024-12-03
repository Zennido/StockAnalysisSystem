import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
import pandas as pd
from sklearn.linear_model import LinearRegression

# Predefined list of popular stocks
STOCK_OPTIONS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA']

# Linked List Implementation for Stock Data
class StockNode:
    def __init__(self, symbol, data):
        self.symbol = symbol  # Stock symbol
        self.data = data  # Stock data (e.g., pandas DataFrame)
        self.next = None  # Link to the next node

class StockLinkedList:
    def __init__(self):
        self.head = None  # Head of the linked list

    def add_stock(self, symbol, data):
        new_node = StockNode(symbol, data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def find_stock(self, symbol):
        current = self.head
        while current:
            if current.symbol == symbol:
                return current.data
            current = current.next
        return None  # Stock not found

# Function to fetch stock data for a specific time range using yfinance
def fetch_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)  
    if not stock_data.empty:
        return stock_data
    else:
        print(f"Error fetching data for {symbol}!")
        return None


# Predictive Analysis (Linear Regression)
def predict_stock_price(df):
    df_copy = df[['Close']].copy()
    df_copy['date'] = (df_copy.index - df_copy.index.min()).days
    
    model = LinearRegression()
    model.fit(df_copy[['date']], df_copy[['Close']])
    
    next_day = [[df_copy['date'].max() + 1]]
    prediction = model.predict(next_day)
    
    return prediction[0][0]

# Visualization function to compare two stocks
def visualize_data(df1, df2, symbol1, symbol2):
    # Create a figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the first stock
    ax.plot(df1.index, df1['Close'], label=f'{symbol1} Close Price', color='blue')
    
    # Plot the second stock
    ax.plot(df2.index, df2['Close'], label=f'{symbol2} Close Price', color='orange')
    
    ax.set_title(f'Comparison of {symbol1} and {symbol2} Stock Prices')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (USD)')
    ax.legend()
    ax.grid(True)
    fig.autofmt_xdate(rotation=45)
    
    # Embed the plot into the GUI using FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

# Function to handle the button click event in GUI
def on_button_click():
    symbol1 = stock_symbol1.get()  # Get the first stock symbol from dropdown
    symbol2 = stock_symbol2.get()  # Get the second stock symbol from dropdown
    start_date = start_date_entry.get()  # Get the start date from the entry
    end_date = end_date_entry.get()  # Get the end date from the entry

    if symbol1 and symbol2 and start_date and end_date:
        # Fetch stock data from the linked list or fetch and store if not found
        df1 = stock_list.find_stock(symbol1)
        df2 = stock_list.find_stock(symbol2)
        
        # If data for the stock is not found in the linked list, fetch it and store
        if df1 is None:
            df1 = fetch_stock_data(symbol1, start_date, end_date)
            if df1 is not None:
                stock_list.add_stock(symbol1, df1)
        
        if df2 is None:
            df2 = fetch_stock_data(symbol2, start_date, end_date)
            if df2 is not None:
                stock_list.add_stock(symbol2, df2)

        if df1 is not None and df2 is not None:
            # Predict stock price for the next day for both stocks
            predicted_price1 = predict_stock_price(df1)
            predicted_price2 = predict_stock_price(df2)
            result_label.configure(
                text=f"Predicted price for {symbol1}: ${predicted_price1:.2f}\n"
                     f"Predicted price for {symbol2}: ${predicted_price2:.2f}")
            
            # Clear previous plots if any
            for widget in app.winfo_children():
                if isinstance(widget, FigureCanvasTkAgg):
                    widget.get_tk_widget().destroy()
            
            # Visualize the data for both stocks in the app
            visualize_data(df1, df2, symbol1, symbol2)


# GUI setup using customtkinter
app = ctk.CTk()

# Set the title and dimensions of the window
app.title("Stock Price Comparison")
app.geometry("600x600")

# Dropdown for first stock symbol
stock_symbol1 = ctk.CTkOptionMenu(app, values=STOCK_OPTIONS)
stock_symbol1.set(STOCK_OPTIONS[0])  # Set default selection
stock_symbol1.pack(pady=20)

# Dropdown for second stock symbol
stock_symbol2 = ctk.CTkOptionMenu(app, values=STOCK_OPTIONS)
stock_symbol2.set(STOCK_OPTIONS[1])  # Set default selection
stock_symbol2.pack(pady=20)

# Label and input field for start date
start_date_label = ctk.CTkLabel(app, text="Start Date (YYYY-MM-DD):")
start_date_label.pack(pady=10)
start_date_entry = ctk.CTkEntry(app)
start_date_entry.pack(pady=5)

# Label and input field for end date
end_date_label = ctk.CTkLabel(app, text="End Date (YYYY-MM-DD):")
end_date_label.pack(pady=10)
end_date_entry = ctk.CTkEntry(app)
end_date_entry.pack(pady=5)


# Button to fetch data and perform analysis
fetch_button = ctk.CTkButton(app, text="Fetch Data and Compare", command=on_button_click)
fetch_button.pack(pady=10)

# Label to display the predicted prices
result_label = ctk.CTkLabel(app, text="Predicted prices for the next day will appear here.")
result_label.pack(pady=20)

# Initialize the linked list for stock data
stock_list = StockLinkedList()

# Run the GUI
app.mainloop()
