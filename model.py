import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

# Read data
df = pd.read_csv('BTCUSDT.csv')

# Data exploration
print(df.head())  # Check the first few rows
print(df.info())  # Check data types and missing values
# Explore further if needed

# Rename columns
df = df[['Open Time','Open']]
df.columns = ['ds', 'y']

# Convert to datetime and float
df['ds'] = pd.to_datetime(df['ds'], format='%Y-%m-%d')
df['y'] = df['y'].astype(float)

# Initialize Prophet model
model = Prophet(yearly_seasonality=True)

# Fit the model
model.fit(df)

# Create future dataframe for forecasting
future = model.make_future_dataframe(periods=14)

# Make predictions
forecast = model.predict(future)

# Plot the forecast
fig = plt.figure(figsize=(10, 6))
plt.plot(df['ds'], df['y'], label='Actual', color='blue')
plt.plot(forecast['ds'], forecast['yhat'], label='Prediction', color='red')
plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='pink', alpha=0.2)
plt.legend()
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('BTCUSDT Price Forecast')
plt.show()
