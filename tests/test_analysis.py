import pytest
import pandas as pd
import numpy as np
from crypto_monitor.analysis.heikin_ashi import HeikinAshi

def test_heikin_ashi_calculation():
    # Create sample price data
    data = pd.DataFrame({
        'open':[10,12,14,11],
        'high': [15, 14, 16, 13],
        'low': [9, 11, 13, 10],
        'close': [12, 14, 11, 12]
    })

    ha = HeikinAshi()
    ha_candles = ha.calculate(data)

    # Test we got the correct shape
    assert len(ha_candles) == len(data)

    # Test that we have all required columns
    required_columns = ['ha_open', 'ha_high', 'ha_low', 'ha_close']
    assert all(col in ha_candles.columns for col in required_columns)

def test_heikin_ashi_trend():
    data = pd.DataFrame({
        'open': [10, 12, 14, 11],
        'high': [15, 14, 16, 13],
        'low': [9, 11, 13, 10],
        'close': [12, 14, 11, 12]
    })

    ha = HeikinAshi()
    ha_candles = ha.calculate(data)
    trends = ha.get_trend_signals(ha_candles)

    assert 'trend' in trends.columns
