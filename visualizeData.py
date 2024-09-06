import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Load the data
csv_file = 'Nat_Gas.csv'
data = pd.read_csv(csv_file, parse_dates=['Dates'])
dates = pd.to_datetime(data['Dates'])
prices = data['Prices']

# Fit SARIMA model
sarima_model = SARIMAX(prices, 
                       order=(1, 1, 1),            # ARIMA(p, d, q)
                       seasonal_order=(1, 1, 1, 12),  # Seasonal ARIMA(P, D, Q, m)
                       enforce_stationarity=False, 
                       enforce_invertibility=False)
sarima_result = sarima_model.fit()

# Forecast the next 12 months
forecast = sarima_result.get_forecast(steps=12)
forecast_prices = forecast.predicted_mean
forecast_conf_int = forecast.conf_int()

# Generate future dates for the next 12 months
future_dates = pd.date_range(start=dates.iloc[-1], periods=12 + 1, freq='ME')[1:]

# Print Historical and Predicted Prices for debugging
print(prices)
print(forecast_prices)

# Plot historical and forecasted data
plt.figure(figsize=(10, 6))
plt.plot(dates, prices, label='Historical Prices')
plt.plot(future_dates, forecast_prices, label='Predicted Prices (Next 12 Months)', linestyle='--')
plt.fill_between(future_dates, forecast_conf_int.iloc[:, 0], forecast_conf_int.iloc[:, 1], color='gray', alpha=0.2)
plt.title('Natural Gas Price Prediction using SARIMA (statsmodels)')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
