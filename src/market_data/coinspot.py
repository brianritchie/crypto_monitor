import requests
from typing import Dict

class CoinspotClient:

    ### Client for interacting with Coinspot's public API

    def __init__(self):
        self.base_url = "https://www.coinspot.com.au/pubapi/v2"

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