import pandas as pd
import os
import sys
from binance import Client
import config

def retrieve_binance_data(symbolList, start_date, end_date):
    # Initialize the Binance client with API keys
    client = Client(config.apiKey, config.secretKey)
        
    # Function to write historical data to a CSV file with filename based on time difference
    def historical_Data_Write_CSV(symbol, candlesticks, start_date, end_date):
        # Creating a DataFrame from the candlestick data
        df = pd.DataFrame(candlesticks, columns=["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"])
        # Converting timestamps to datetime format
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms').dt.date  # Only date without time
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
        # Generating a filename based on symbol
        filename = f"{symbol}.csv"
        # Writing the DataFrame to a CSV file
        df.to_csv(filename, index=False)
    
    # Loop through each symbol in the symbol list and retrieve historical data
    for symbol in symbolList:
        print("DATA RETRIEVAL: ", symbol)
        # Retrieve historical candlestick data from Binance API
        candlesticks = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_, start_date, end_date)
        # Write the retrieved data to a CSV file with filename based on time difference and symbol
        historical_Data_Write_CSV(symbol, candlesticks, start_date, end_date)
    
    # Sound alert to indicate that data retrieval process is complete


# Örnek kullanım
symbolList = ["BTCUSDT"]  # Symbol list , "XRPUSDT", "BNBUSDT"
start_date = "2023-01-01"  # Start date
end_date = "2024-03-04"  # End date
retrieve_binance_data(symbolList, start_date, end_date)
