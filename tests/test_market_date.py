import pytest
from crypto_monitor.market_data.coinspot import CoinspotClient

def test_coinspot_client_initialization():
    client = CoinspotClient()
    assert client is not None

def test_fetch_btc_latest():
    client = CoinspotClient()
    latest = client.get_latest_price('BTC')

    # Test response structure matches API documentation
    assert isinstance(response, dict)
    assert 'status' in response
    assert 'message' in response
    assert 'prices' in response

    # Test prices object structure
    assert 'bid' in response['prices']
    assert 'ask' in response['prices']
    assert 'last' in response['prices']

def test_invalid_coin_handling():
    client = CoinspotClient()
    with pytest.raises(ValueError):
        client.get_latest_price('') # Empty string should raise error