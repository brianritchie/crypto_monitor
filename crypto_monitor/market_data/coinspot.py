import requests
import pandas as pd
from datetime import datetime
from collections import deque
from typing import Dict, Deque

class CoinspotClient:

    ### Client for interacting with Coinspot's public API

    def __init__(self, max_history: int = 100):
        self.base_url = "https://www.coinspot.com.au/pubapi/v2"
        self._price_history: Dict[str, Deque] = {}
        self.max_history = max_history

    def _init_history(self, coin:str):
        #Initialize history for coin if it doesn't exist
        if coin not in self._price_history:
            self._price_history[coin] = deque(maxlen=self.max_history)

    def add_price_to_history(self, coin: str, price_data: Dict):
        #Add a price point to the historical data
        self._init_history(coin)

        timestamp = datetime.now()
        data_point = {
            'timestamp': timestamp,
            'open': float(price_data['prices']['bid']),
            'high': float(price_data['prices']['ask']),
            'low': float(price_data['prices']['bid']),
            'close': float(price_data['prices']['last'])
        }

        self._price_history[coin].append(data_point)

    def get_price_history(self, coin: str) -> pd.DataFrame:
        # Get historical price data as a DataFrame
        if coin not in self._price_history:
            return pd.DataFrame()
        
        df = pd.DataFrame(list(self._price_history[coin]))
        if not df.empty:
            df.set_index('timestamp', inplace=True)
        return df

    def get_latest_price(self, coin: str) -> Dict:
        if not coin:
            raise ValueError("Coin symbol cannot be empty")
        
        coin = coin.upper()  # Ensure uppercase for consistency
        endpoint = f"/latest/{coin}"

        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            response.raise_for_status() # Raises exception for 4XX/5XX status codes
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch price for {coin}: {str(e)}")

    def format_price_data(self, response: Dict) -> Dict:
        if response['status'] != 'ok':
            raise ValueError(f"API Error: {response['message']}")
        
        return {
            'symbol': 'BTC', # We'll extend this later
            'bid': float(response['prices']['bid']),
            'ask': float(response['prices']['ask']),
            'last': float(response['prices']['last']),
            'spread': float(response['prices']['ask']) - float(response['prices']['bid'])
        }