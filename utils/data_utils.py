import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import schwabdev
from datetime import datetime
import streamlit as st
from typing import List
from collections import defaultdict
import json


def filter_chain(chain: pd.DataFrame):
    '''
    Filter the option chain to only include the necessary columns. 
    '''
    relevant_columns = [
    'symbol', 'description', 'strikePrice', 
    'bid', 'ask', 'last', 'mark', 
    'delta', 'gamma', 'theta', 'vega', 'rho', 
    'inTheMoney', 'intrinsicValue', 'extrinsicValue', 'daysToExpiration'
    ]

    newchain = chain[relevant_columns]

    renamed_columns = [
        'Contract Name', 'Description', 'Strike', 
        'Bid', 'Ask', 'Last', 'Mark', 
        'Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 
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

        return opt_dict
    
    def get_price(self, ticker:str):
        '''
        Get last price of the security.
        '''
        quote = self.client.quote(ticker).json()

        return quote[ticker]['quote']['lastPrice']

class DummyData:
    def __init__(self):
        
        self.demo = True
        return
    
    def get_options_chain_dict(self, ticker:str) -> dict:
        opt_dict = {'calls':defaultdict(list), 
                    'puts':defaultdict(list)}
        
        # Only have AAPL data for demo purposes
        with open('data\\dummy_data\\AAPL.json') as f:
            json_data = json.load(f)
            
        for type in ['callExpDateMap', 'putExpDateMap']:
            for expdate in json_data[type]:
                records = []
                for k in json_data[type][expdate]:
                    data = json_data[type][expdate][k][0]
                    records.append(data)
                df=pd.DataFrame(records)
                opt_dict[type.split('ExpDateMap')[0]+'s'][convert_date(expdate)] = filter_chain(df)

        return opt_dict
        

    def get_price(self, ticker:str):
        '''
        Get last price of the security.
        '''
        return 229.40





if __name__ == '__main__':
    #print(get_options_date('AAPL'))
    myclient = DummyData()
    aapldata = myclient.get_options_chain_dict('AAPL')
    print(aapldata['puts'])