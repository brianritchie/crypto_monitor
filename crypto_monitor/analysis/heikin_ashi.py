import pandas as pd
import numpy as np
from typing import Dict, List

class HeikinAshi:

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        ha_df = df.copy()

        #Calculate HeikinAshi values
        ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

        # Calculate HA open - first row uses original opening price
        ha_df['ha_open'] = df['open'].copy()
        for i in range(1, len(df)):
            ha_df.loc[df.index[i], 'ha_open'] = (
                ha_df.loc[df.index[i-1], 'ha_open'] + ha_df.loc[df.index[i-1], 'ha_close']
            )/2

        # Calculate HA high and low
        ha_df['ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].max(axis=1)
        ha_df['ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].min(axis=1)

        return ha_df
    
    def get_trend_signals(self, ha_df: pd.DataFrame) -> pd.DataFrame:
        df = ha_df.copy()

        # Define trend based on HA candle characteristics
        df['trend'] = 'neutral'

        # Bullish Signals
        bullish_mask = (
            (df['ha_close'] > df['ha_open']) & (df['ha_low'] == df['ha_open']) # No lower shadow
        )
        df.loc[bullish_mask, 'trend'] = 'bullish'

        # Bearish signals
        bearish_mask = (
            (df['ha_close'] < df['ha_open']) & (df['ha_high'] == df['ha_open']) # No upper shadow
        )
        df.loc[bearish_mask, 'trend'] = 'bearish'

        return df