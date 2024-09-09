import requests
import json

class DataManager:
    def __init__(self, api_url):
        self.api_url = api_url

    def fetch_stock_data(self, stock_symbol):
        response = requests.get(f'{self.api_url}/stock/{stock_symbol}')
        data = response.json()
        self.save_data(stock_symbol, data)
        return data

    def save_data(self, stock_symbol, data):
        with open(f'data/{stock_symbol}.json', 'w') as file:
            json.dump(data, file)