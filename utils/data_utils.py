import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import schwabdev
from datetime import datetime
from typing import List
from collections import defaultdict
import json
from pathlib import Path
from pytz import timezone


def filter_chain(chain: pd.DataFrame):
    '''
    Filter the option chain to only include the necessary columns. Returns dataframe with 
    the option Contract Name, Description (information about option expiration, strike, as listed), 
    Strike price, Bid, Ask, Last, Mark, Delta, Gamma, Theta, Vega, Rho, Volatility, ITM (boolean flag for in-the-money),
    Intrinsic Value, Extrinsic Value, and Days to Expiration (not annualized). 
    ### Parameters:
    - chain: pd.DataFrame: Raw option chain data from Schwab API, formatted in the SchwabData class.
    '''
    relevant_columns = [
    'symbol', 'description', 'strikePrice', 
    'bid', 'ask', 'last', 'mark', 
    'delta', 'gamma', 'theta', 'vega', 'rho', 'volatility',
    'inTheMoney', 'intrinsicValue', 'extrinsicValue', 'daysToExpiration'
    ]

    newchain = chain[relevant_columns]

    renamed_columns = [
        'Contract Name', 'Description', 'Strike', 
        'Bid', 'Ask', 'Last', 'Mark', 
        'Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'Volatility',
        'ITM', 'Intrinsic Value', 'Extrinsic Value', 'Days to Expiration'
        ]
    newchain.columns = renamed_columns
    
    return newchain

def is_market_open():
    eastern = timezone('US/Eastern')
    now = datetime.now(eastern)
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= now <= market_close

def convert_date(date:str):
    '''
    Convert date from Schwab API format to a more readable format.
    ### Parameters:
    - date: str: Date in the format "YYYY-MM-DD:HH:MM:SS-05:00".
    '''
    date = date.split(":")[0]
    return datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")


class SchwabData:
    '''
    Class to interact with the Schwab API. Based off of the schwabdev package. Takes no parameters. 

    ### Attributes:
    - app_key: app key for the Schwab API. Kept in the .env file.
    - secret: secret key for the Schwab API. Kept in the .env file.
    - client: Schwab API client object.

    ### Methods:
    - get_options_chain_dict(ticker:str) -> dict: Get options chain and interest rate. Returns
    a tuple of a dictionary with the options chain and the risk-free interest rate.
    - get_price(ticker:str): Get last price of the security. Returns float. 
    - get_div_yield(ticker:str): Get the current dividend yield of chosen stock. Returns float.
    '''
    def __init__(self):
        load_dotenv()

        self.app_key = os.getenv('APP_KEY')
        self.secret = os.getenv('SECRET_KEY')

        self.client = schwabdev.Client(app_key=self.app_key, app_secret=self.secret)

        return
    
    def get_options_chain_dict(self, ticker:str) -> tuple[dict[pd.DataFrame], float]:
        '''
        Get options chain and interest rate. Gets raw data using Schwab API client, 
        then filters the data to separate into calls and puts and filter necessary columns.
        Also gets the risk-free interest rate. Returns a tuple of a dictionary with the options chain and the risk-free interest rate.
        ### Parameters:
        - ticker: str: Ticker symbol of the security (e.g. AAPL, MSFT, TSLA).
        '''
        opt_dict = {'calls':defaultdict(list), 
                    'puts':defaultdict(list)}
        #q: Defaultdict of dict then of lists?
        #a: 
        json_data = self.client.option_chains(ticker).json()

        if 'errors' in json_data.keys():
            raise ValueError('Invalid ticker symbol. Please try again.')
        else:
            for type in ['callExpDateMap', 'putExpDateMap']:
                for expdate in json_data[type]:
                    records = []
                    for k in json_data[type][expdate]:
                        data = json_data[type][expdate][k][0]
                        records.append(data)
                    df=pd.DataFrame(records)
                    opt_dict[type.split('ExpDateMap')[0]+'s'][convert_date(expdate)] = filter_chain(df)

        interest_rate = json_data['interestRate']

        return opt_dict, interest_rate

    def get_price(self, ticker:str) -> float:
        '''
        Get last price of the security. Returns float.
        ### Parameters:
        - ticker: str: Ticker symbol of the security (e.g. AAPL, MSFT, TSLA).
        '''
        quote = self.client.quote(ticker).json()

        return quote[ticker]['quote']['lastPrice']

    def get_div_yield(self, ticker:str) -> float:
        '''
        Get the current dividend yield of chosen stock. Returns float.
        ### Parameters:
        - ticker: str: Ticker symbol of the security (e.g. AAPL, MSFT, TSLA).
        '''
        quote = self.client.quote(ticker).json()

        return quote[ticker]['fundamental']['divYield']/100 # originally in percent


class DummyData:
    '''
    Dummy class to mimic Schwab API client if user is in demo mode. Takes no parameters, has no attributes.
    Directly reads from the dummy data kept in "data\dummy_data\AAPL.json".

    ### Methods:
    - get_options_chain_dict(ticker:str) -> dict: Get options chain based on dummy AAPL data and a fixed 
    interest rate. Returns a tuple of a dictionary with the options chain and the risk-free interest rate.
    - get_price(ticker:str): Get last price of the security, based on fixed value of 229.40. Returns float. 
    - get_div_yield(ticker:str): Get the dummy dividend yield of AAPL, set at 0.00403. Returns float.
    '''
    def __init__(self):
        
        return
    
    def get_options_chain_dict(self, ticker:str) -> dict:
        opt_dict = {'calls':defaultdict(list), 
                    'puts':defaultdict(list)}

        # Only have AAPL data for demo purposes
        cwd = Path.cwd()
        appl_dummy_path = cwd / 'data' / 'dummy_data' / 'AAPL.json'
        with open(appl_dummy_path) as f:
            json_data = json.load(f)
            
        for type in ['callExpDateMap', 'putExpDateMap']:
            for expdate in json_data[type]:
                records = []
                for k in json_data[type][expdate]:
                    data = json_data[type][expdate][k][0]
                    records.append(data)
                df=pd.DataFrame(records)
                opt_dict[type.split('ExpDateMap')[0]+'s'][convert_date(expdate)] = filter_chain(df)

        interest_rate = 0.045

        return opt_dict, interest_rate
        

    def get_price(self, ticker:str):
        '''
        Get last price of the security. Fixed at 229.40.
        '''
        return 229.40
    
    def get_div_yield(self, ticker:str):
        '''
        Get the dividend yield. Fixed at 0.00403.
        '''
        return 0.403/100 # originally in percent


if __name__ == '__main__':
    #print(get_options_date('AAPL'))
    myclient = DummyData()
    aapldata = myclient.get_options_chain_dict('AAPL')
    print(aapldata['puts'])