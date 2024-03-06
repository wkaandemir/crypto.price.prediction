import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QCalendarWidget, QMessageBox, QLineEdit
from PyQt5.QtCore import QDate
import pandas as pd
from binance import Client
import config
import matplotlib.pyplot as plt
from prophet import Prophet
from PyQt5.QtGui import QIntValidator


class CryptoAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cryptocurrency Data Analysis Application")
        self.initUI()
        self.df = None
    
    def initUI(self):
        # Label and ComboBox for Cryptocurrency Pair
        self.pair_label = QLabel("Select Cryptocurrency Pair:")
        self.pair_combobox = QComboBox()
        self.pair_combobox.addItems(["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT"])  # Example pairs added
        
        # Second pair label and combobox
        self.pair_label2 = QLabel("Select Time Scale:")
        self.pair_combobox2 = QComboBox()
        self.pair_combobox2.addItems(["1 Minute", "3 Minutes", "5 Minutes", "15 Minutes", "30 Minutes",
                                    "1 Hour", "2 Hours", "4 Hours", "6 Hours", "8 Hours", 
                                    "12 Hours", "1 Day", "1 Week", "1 Month"])  # Example intervals added
        
        self.pair_label3 = QLabel("Select Prediction Timeframe:")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Enter prediction timeframe (Days)")  # Example placeholder text
        validator = QIntValidator()
        self.time_input.setValidator(validator)


        # Calendar for start date
        self.start_date_label = QLabel("Start Date:")
        self.start_calendar = QCalendarWidget()
        
        # Calendar for end date
        self.end_date_label = QLabel("End Date:")
        self.end_calendar = QCalendarWidget()
        
        # Button to start analysis
        self.analyze_button = QPushButton("Generate Prediction")
        self.analyze_button.clicked.connect(self.create_prediction)
        
        # Button to fetch data
        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self.get_data)
        
        # Layout
        pair_layout = QHBoxLayout()
        pair_layout.addWidget(self.pair_label)
        pair_layout.addWidget(self.pair_combobox)
        pair_layout.addWidget(self.pair_label2)  # Add second pair label
        pair_layout.addWidget(self.pair_combobox2)  # Add second pair combobox
        pair_layout.addWidget(self.time_input) # Add time_input
        
        date_layout = QHBoxLayout()  # Changed to QHBoxLayout
        date_layout.addWidget(self.start_date_label)
        date_layout.addWidget(self.start_calendar)
        date_layout.addWidget(self.end_date_label)
        date_layout.addWidget(self.end_calendar)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.fetch_button)  # Add fetch button
        button_layout.addWidget(self.analyze_button)

        
        main_layout = QVBoxLayout()
        main_layout.addLayout(pair_layout)
        main_layout.addLayout(date_layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def get_data(self):
        # Get the selected cryptocurrency pair from the combobox
        crypto_pair = self.pair_combobox.currentText()
        # Get the selected time scale
        time_scale = self.pair_combobox2.currentText()
        # Get the selected start date
        start_date = self.start_calendar.selectedDate().toString("yyyy-MM-dd")
        # Get the selected end date
        end_date = self.end_calendar.selectedDate().toString("yyyy-MM-dd")
        
        # Determine the KLINE_INTERVAL based on the selected time scale
        kline_intervals = {
            "1 Minute": Client.KLINE_INTERVAL_1MINUTE,
            "3 Minutes": Client.KLINE_INTERVAL_3MINUTE,
            "5 Minutes": Client.KLINE_INTERVAL_5MINUTE,
            "15 Minutes": Client.KLINE_INTERVAL_15MINUTE,
            "30 Minutes": Client.KLINE_INTERVAL_30MINUTE,
            "1 Hour": Client.KLINE_INTERVAL_1HOUR,
            "2 Hours": Client.KLINE_INTERVAL_2HOUR,
            "4 Hours": Client.KLINE_INTERVAL_4HOUR,
            "6 Hours": Client.KLINE_INTERVAL_6HOUR,
            "8 Hours": Client.KLINE_INTERVAL_8HOUR,
            "12 Hours": Client.KLINE_INTERVAL_12HOUR,
            "1 Day": Client.KLINE_INTERVAL_1DAY,
            "1 Week": Client.KLINE_INTERVAL_1WEEK,
            "1 Month": Client.KLINE_INTERVAL_1MONTH
        }
        kline_interval = kline_intervals.get(time_scale, Client.KLINE_INTERVAL_1MINUTE)
        
        # Call function to start analysis with the selected cryptocurrency pair and dates
        print("Analysis started. Cryptocurrency Pair:", crypto_pair)
        print("Start Date:", start_date)
        print("End Date:", end_date)
        print("Time Interval:", kline_interval)
        
        client = Client(config.apiKey, config.secretKey)
        
        # Retrieve historical candlestick data from Binance API
        candlesticks = client.get_historical_klines(crypto_pair, kline_interval, start_date, end_date)
        
        # Function to write historical data to a CSV file with filename based on time difference
        df = pd.DataFrame(candlesticks, columns=["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"])
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms').dt.date  # Only date without time
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
        
        # Sound alert to indicate that data retrieval process is complete
        print("Data retrieval process complete.")
        QMessageBox.information(self, "Information", "Data retrieval process complete.")
        
        self.df = df

    def create_prediction(self):
        if self.df is not None:
            future_time = int(self.time_input.text())
            crypto_pair = self.pair_combobox.currentText()
            # Print the DataFrame

            df = self.df[['Open Time','Open']]
            df.columns = ['ds', 'y']
            df.loc[:, 'ds'] = pd.to_datetime(df['ds'], format='%Y-%m-%d')
            df.loc[:, 'y'] = df['y'].astype(float)

            # Initialize Prophet model
            model = Prophet(yearly_seasonality=True)

            # Fit the model
            model.fit(df)

            # Create future dataframe for forecasting
            future = model.make_future_dataframe(periods=future_time)

            # Make predictions
            forecast = model.predict(future)

            # Plot the forecast
            plt.plot(df['ds'], df['y'], label='Actual', color='blue')
            plt.plot(forecast['ds'], forecast['yhat'], label='Prediction', color='red')
            plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='pink', alpha=0.2)
            plt.legend()
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title(f'Price Prediction Data for {crypto_pair}') # Setting plot title
            plt.show()



        else:
            QMessageBox.information(self, "Information", "Data not fetched, so printing operation could not be performed.")
        
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    crypto_app = CryptoAnalysisApp()
    crypto_app.show()
    sys.exit(app.exec_())
