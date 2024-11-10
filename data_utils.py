import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import schwabdev
from datetime import datetime
import streamlit as st
from typing import List

load_dotenv()

app_key = os.getenv('APP_KEY')
secret = os.getenv('SECRET_KEY')

client = schwabdev.Client(app_key=app_key, app_secret=secret)

@st.cache_data
def get_options_chain(ticker, strategy: str, expiration: str):
    '''
    User enters a stock and the type of option chain they are looking for (long call, long put) and the function returns the chain. 
    '''
    chain = pd.DataFrame()
    expiration = datetime.strptime(expiration, "%m/%d/%Y").strftime("%Y-%m-%d")
    if strategy == "Long Call":
        optdata = client.option_chains(ticker, 'CALL', toDate=expiration, fromDate=expiration).json()
        expdatemap = next(iter(optdata['callExpDateMap'].values()))
        records = [item[0] for item in expdatemap.values()]
        chain = pd.DataFrame(records)

    elif strategy == "Long Put":
        optdata = client.option_chains(ticker, 'PUT', toDate=expiration, fromDate=expiration).json()
        expdatemap = next(iter(optdata['putExpDateMap'].values()))
        records = [item[0] for item in expdatemap.values()]
        chain = pd.DataFrame(records)

    # chain['Name'] = chain['Contract Name'].apply(plot.transcribe_option)
    # cols = chain.columns.tolist()
    # cols = cols[-1:] + cols[:-1]
    # chain = chain[cols]
    
    return filter_chain(chain)

def get_options_date(ticker: str) -> List[str]:
    '''
    Get the possible option expiration dates for a given stock using SchwabDev. 
    '''
    try:
        dates_json = client.option_expiration_chain(ticker).json()
        dates = pd.json_normalize(dates_json['expirationList'], sep='_')['expirationDate'].to_list()
        return [datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y") for date in dates]
    # callExpDateMap = dates_json['callExpDateMap']
    # putExpDateMap = dates_json['putExpDateMap']
    # if len(callExpDateMap) > len(putExpDateMap):
    #     dates = list(callExpDateMap.keys())
    # else:
    #     dates = list(putExpDateMap.keys())
    # return dates
    except KeyError:
        st.error('Chosen ticker is invalid, please try with a different one.')
        return []

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

def get_price(ticker:str):
    '''
    Get last price of the security.
    '''
    quote = client.quote(ticker).json()

    return quote[ticker]['quote']['lastPrice']


if __name__ == '__main__':
    print(get_options_date('AAPL'))