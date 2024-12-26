import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class VolumeAnalyzer:
    ## Analyze volume profile and order book imbalances

    def __init__(self, price_levels: int = 10):
        self.price_levels = price_levels
    
    def analyze_order_book(self, buy_orders: List[Dict], sell_orders: List[Dict]) -> Dict:
        # Analyze order book for imbalances

        if not buy_orders or not sell_orders:
            return {
                'imbalance_ratio': 0,
                'buy_volume': 0,
                'sell_volume': 0,
                'dominant_side': 'neutral'
            }
        
        # Calculate total volumes
        buy_volume = sum(float(order['amount']) * float(order['rate']) for order in buy_orders)
        sell_volume = sum(float(order['amount']) * float(order['rate']) for order in sell_orders)

        # Calculate imbalance ratio
        total_volume = buy_volume + sell_volume
        if total_volume > 0:
            imbalance_ratio = (buy_volume - sell_volume) / total_volume
        else:
            imbalance_ratio = 0

        # Determine dominant side
        if imbalance_ratio > 0.2:
            dominant_side = 'buy'
        elif imbalance_ratio < -0.2:
            dominant_side = 'sell'
        else:
            dominant_side = 'neutral'

        return {
            'imbalance_ratio': imbalance_ratio,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'dominant_side': dominant_side
        }
    
    def calculate_vbp(self, df: pd.DataFrame) -> Dict:
        # Calculate Volume by Price Profile

        if df.empty:
            return{}
        
        # Create price bins
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_range = price_max - price_min
        bin_size = price_range / self.price_levels

        # Create bins and calculate volume for each
        price_bins = []
        volume_profile = []

        for i in range(self.price_levels):
            bin_low = price_min + (i * bin_size)
            bin_high = bin_low + bin_size

            # Filter trades in this price range
            mask = (df['low'] >= bin_low) & (df['high'] < bin_high)
            volume_in_bin = df[mask]['volume'].sum() if 'volume' in df else len(df[mask])

            price_bins.append(f"{bin_low:.2f}-{bin_high:.2f}")
            volume_profile.append(volume_in_bin)

        # Find Point of Control (POC) - price level with highest volume
        poc_index = np.argmax(volume_profile)
        poc_price_range = price_bins[poc_index]

        return {
            'price_bins': price_bins,
            'volume_profile': volume_profile,
            'poc': poc_price_range,
            'poc_volume': volume_profile[poc_index]
        }
    
    def get_volume_signals(self, vbp_data: Dict, order_book_data: Dict) -> str:
        ## Generate trading signals based on volume analysis

        if not vbp_data or not order_book_data:
            return "Insufficient data for volume analysis"
        
        signals = []

        # Order book imbalance signals
        if order_book_data['imbalance_ratio'] > 0.2:
            signals.append("Strong buying pressure")
        elif order_book_data['imbalance_ratio'] < -0.2:
            signals.append("Strong selling pressure")
        
        # Volume concentration signals
        if vbp_data['volume_profile']:
            max_vol = max(vbp_data['volume_profile'])
            avg_vol = sum(vbp_data['volume_profile']) / len(vbp_data['volume_profile'])

            if max_vol > 2 * avg_vol:
                signals.append(f"High volume concentration at {vbp_data['poc']}")
            
        return " • ".join(signals) if signals else "No significant volume signals"