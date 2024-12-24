import click
from crypto_monitor.market_data.coinspot import CoinspotClient

@click.command()
@click.option('--coin', default='BTC', help='Cryptocurrency symbol (e.g., BTC, XRP)')

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
    get_price()