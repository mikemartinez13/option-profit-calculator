import requests
import math
import numpy as np
from scipy.stats import norm

#Alpha Vantage Stock API Key: 42IHQ5T9TB4C28H0
API_KEY = '42IHQ5T9TB4C28H0'

def get_current_price(symbol):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    if 'Global Quote' in data:
        return float(data['Global Quote']['05. price'])
    else:
        return None


def get_historical_prices(symbol, outputsize='compact'):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={outputsize}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    if 'Time Series (Daily)' in data:
        prices = [float(data['Time Series (Daily)'][date]['4. close']) for date in sorted(data['Time Series (Daily)'].keys())]
        return prices
    else:
        return None

#Calculate Sigma

def hist_volatility(prices):
    """
    Calculate sigma (volatility) based on historical volatility for a specified historical period.
    
    Args:
    prices (list or numpy array): List or array of historical prices of the underlying asset.
    
    Returns:
    float: Sigma (volatility) based on historical volatility.
    """
    prices_array = np.array(prices)
    # Calculate logarithmic returns
    returns = np.log(prices_array[1:] / prices_array[:-1])
    
    # Calculate standard deviation of returns (volatility)
    sigma = np.std(returns)
    
    # Annualize volatility for 1 year
    sigma_annualized = sigma * np.sqrt(252)  # Assuming 252 trading days in a year
    
    return sigma_annualized

#Long Call
def Long_Call(price, ticker, T): #Binomial Option Model for American Style (Early Exercise)
    """
    Calculate the theoretical price of a long call option using the Binomial Option Pricing Model.
    
    Args:
    - price: Option Strike Price
    - ticker: Ticker symbol of the underlying asset
    - T: Time to Expiration in years
    
    Returns:
    float: Theoretical price of the long call option.
    """
    S = get_current_price(ticker)  # The Current (Live) price of the stock
    K = price  # Option Strike Price
    r = 0.55  # Risk Free Interest Rate (e.g., US Central Bank rate)

    # Calculate volatility using historical data
    prices = get_historical_prices(ticker)
    sigma = hist_volatility(prices)

    # Number of time steps in the binomial model
    N = 100  # You can adjust this value for more accuracy

    # Time step
    dt = T / N

    # Discount factor
    df = np.exp(-r * dt)

    # Up and Down factors
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u

    # Probabilities of up and down movements
    p = (np.exp(r * dt) - d) / (u - d)

    # Initialize option price at each node
    option_prices = np.zeros(N + 1)

    # Calculate option prices at expiration
    for i in range(N + 1):
        option_prices[i] = max(0, S * (u ** (N - i)) * (d ** i) - K)

    # Backward induction to calculate option prices at earlier time points
    for j in range(N - 1, -1, -1):
        for i in range(j + 1):
            option_prices[i] = max(0, df * (p * option_prices[i] + (1 - p) * option_prices[i + 1]))

    # Option price at time 0
    call_price = option_prices[0]

    return call_price

#European Style Black Sholes Model (No Early Exercise)
# def Long_Call(price, ticker):
#     """
#     Calculate the theoretical price of a long call option using the Black-Scholes model.
    
#     Returns:
#     float: Theoretical price of the long call option.
#     """
#     ticker = 'MSFT' #REPLACE THIS WITH OTHER CLASS THAT GETS THE TICKER FROM USER (UI)
#     S = get_current_price(ticker) #The Current (Live) price of the stock
#     K = price #Option Strike Price; REPLACE w/ actual option strike price desired by User!
#     r = 0.55 #Risk Free Interest Rate, we use US Central Bank rate
#     T = 0.5 #Time to Expiration in years; REPLACE w/ USER input!

#     prices = get_historical_prices(ticker)
#     sigma = hist_volatility(prices) #Volatility of the underlying asset (annualized, expressed as a decimal). We use historical volatility in our model calculation
#     #This involves computing the standard deviation of the logarithmic returns of the asset over a specified historical period (e.g., 30 days, 90 days, 1 year)
#     #We use 1 year period

#     d1 = (math.log(S / K) + (r + (sigma ** 2) / 2) * T) / (sigma * math.sqrt(T))
#     d2 = d1 - sigma * math.sqrt(T)
    
#     call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    
#     return call_price

print("Long Call: ")
print(Long_Call(174, 'aapl', 1/365))

def Long_Put(price, ticker, T):
    """
    Calculate the theoretical price of a long put option using the Black-Scholes model.
    
    Args:
    - price: Option Strike Price
    - ticker: Ticker symbol of the underlying asset
    - T: Time to Expiration in years
    
    Returns:
    float: Theoretical price of the long put option.
    """
    S = get_current_price(ticker)  # The Current (Live) price of the stock
    K = price  # Option Strike Price
    r = 0.55  # Risk Free Interest Rate (e.g., US Central Bank rate)

    # Calculate volatility using historical data
    prices = get_historical_prices(ticker)
    sigma = hist_volatility(prices)

    d1 = (math.log(S / K) + (r + (sigma ** 2) / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return put_price

print("Long Put: ")
print(Long_Put(174, 'aapl', 1/365))