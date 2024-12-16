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


def filter_chain(chain: pd.DataFrame):
    '''
    Filter the option chain to only include the necessary columns. 
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


def convert_date(date:str):
    #q: If a date has a format like this '2024-11-15:5', how do I strip the :5? 
    # a: Use the split method
    date = date.split(":")[0]
    return datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")


class SchwabData:
    def __init__(self):
        load_dotenv()

        self.app_key = os.getenv('APP_KEY')
        self.secret = os.getenv('SECRET_KEY')

        self.client = schwabdev.Client(app_key=self.app_key, app_secret=self.secret)
        self.demo = False

        return
    
    def get_options_chain_dict(self, ticker:str) -> dict:
        '''
        Get options chain and interest rate. 
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
    
    def get_price(self, ticker:str):
        '''
        Get last price of the security.
        '''
        quote = self.client.quote(ticker).json()

        return quote[ticker]['quote']['lastPrice']
    
    def get_div_yield(self, ticker:str):
        '''
        Get the current interest rate.
        '''
        quote = self.client.quote(ticker).json()

        return quote[ticker]['fundamental']['divYield']/100 # originally in percent


class DummyData:
    def __init__(self):
        
        self.demo = True
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
        Get last price of the security.
        '''
        return 229.40
    
    def get_div_yield(self, ticker:str):
        '''
        Get the current interest rate.
        '''

        return 0.403/100 # originally in percent





if __name__ == '__main__':
    #print(get_options_date('AAPL'))
    myclient = DummyData()
    aapldata = myclient.get_options_chain_dict('AAPL')
    print(aapldata['puts'])