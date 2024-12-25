import click
import time
from crypto_monitor.market_data.coinspot import CoinspotClient
from crypto_monitor.analysis.heikin_ashi import HeikinAshi

@click.command()
@click.option('--coin', default='BTC', help='Cryptocurrency symbol (e.g., BTC, XRP)')
@click.option('--interval', default=60, help='Update interval in seconds')
@click.option('--duration', default=10, help='How many intervals to run for')

def monitor_price(coin: str, interval: int, duration: int):
    client = CoinspotClient()
    ha_analyzer = HeikinAshi()

    click.echo(f"\nMonitoring {coin} price every {interval} seconds...")

    for _ in range(duration):
        try:
            # Fetch and store price
            response = client.get_latest_price(coin)
            client.add_price_to_history(coin, response)

            # Get price history and calculate HA
            df = client.get_price_history(coin)
            if not df.empty:
                ha_df = ha_analyzer.calculate(df)
                ha_df = ha_analyzer.get_trend_signals(ha_df)

                # Get latest data point
                latest = ha_df.iloc[-1]

                click.echo(f"\nTimestamp: {df.index[-1]}")
                click.echo(f"Price: ${latest['close']:,.2f}")
                click.echo(f"Trend: {latest['trend'].upper()}")

            time.sleep(interval)

        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)
            break


def get_price(coin):
    client = CoinspotClient()
    try:
        response = client.get_latest_price(coin)
        formatted = client.format_price_data(response)

        click.echo(f"\n{coin} Price Information:")
        click.echo(f"Bid: ${formatted['bid']:,.2f}")
        click.echo(f"Ask: ${formatted['ask']:,.2f}")
        click.echo(f"Last: ${formatted['last']:,.2f}")
        click.echo(f"Spread: ${formatted['spread']:,.2f}\n")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    monitor_price()