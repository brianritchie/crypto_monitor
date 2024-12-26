import pandas as pd
import numpy as np
from typing import Dict, Optional

class SpreadAnalyzer:
    ## Analyzes bid-ask spreads to determine market liquidity conditions

    def __init__(self):
        # Default thresholds in percentage
        self.default_thresholds = {
            'tight': 0.1, # 0.1% spread
            'normal': 0.5, # 0.5% spread
            'wide': 1.0 # 1.0% spread
        }

        # Coin-specific thresholds
        self.coin_thresholds = {
            'BTC': {'tight': 0.05, 'normal': 0.2, 'wide': 0.5},
            'XRP': {'tight': 0.2, 'normal': 1.0, 'wide': 2.0}
        }

    def get_thresholds(self,coin: str) -> Dict[str, float]:
        # Get appropriate thresholds for a given coin
        return self.coin_thresholds.get(coin, self.default_thresholds)
        
    def calculate_volatility(self, df: pd.DataFrame) -> Optional[float]:
        # Calculate price volatility using spread data
        if df.empty or len(df) < 2:
            return None
            
            return df['spread_percentage'].std()
        
    def analyze_spread(self, df: pd.DataFrame, coin: str) -> Dict:
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        thresholds = self.get_thresholds(coin)

        # Calculate spread statistics
        spread_stats = {
            'current_spread': latest['spread_absolute'],
            'current_spread_percentage': latest['spread_percentage'],
            'avg_spread': df['spread_absolute'].mean(),
            'avg_spread_percentage': df['spread_percentage'].mean(),
            'max_spread': df['spread_absolute'].max(),
            'min_spread': df['spread_absolute'].min(),
            'volatility': self.calculate_volatility(df)
        }

        # Determine market condition
        if latest['spread_percentage'] <= thresholds['tight']:
            condition = 'TIGHT'
            message = 'High liquidity = favorable trading conditions'
        elif latest['spread_percentage'] <= thresholds['normal']:
            condition = 'NORMAL'
            message = 'Normal market conditions'
        else:
            condition = 'WIDE'
            message = 'Low liquidity - exercise caution'

        spread_stats.update({
            'condition': condition,
            'message': message
        })

        return spread_stats