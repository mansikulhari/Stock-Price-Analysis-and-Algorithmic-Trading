import yfinance as yf
from prophet import Prophet



from matplotlib import pyplot as plt
from prophet.plot import plot_plotly, plot_components_plotly

symbol = 'AAPL'

# Train data must have 'ds' column with the dates and 'y' as the values for Prophet to work
train_data = yf.download(symbol, start='2010-09-01', end='2020-09-01')
train_data.reset_index(inplace=True)
train_data = train_data[['Date', 'Close']]
train_data.columns = ['ds', 'y']

test_data = yf.download(symbol, start='2020-09-02', end='2021-09-01')
test_data.reset_index(inplace=True)
test_data = test_data[['Date', 'Close']]
test_data.columns = ['ds', 'y']

# Training the model
m = Prophet()
m = Prophet(daily_seasonality=True)
m.fit(train_data)

# Making predictions
future = m.make_future_dataframe(periods=365)
forecast = m.predict(future)

# Plotting the results

plt.plot(train_data['ds'], train_data['y'], label='Train')
plt.plot(test_data['ds'], test_data['y'], label='Test')
plt.plot(forecast['ds'], forecast['yhat'], label='Predicted')
plt.legend()
plt.show()

