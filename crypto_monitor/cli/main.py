import click
import time
from rich.console import Console
from rich.table import Table
from crypto_monitor.market_data.coinspot import CoinspotClient
from crypto_monitor.analysis.heikin_ashi import HeikinAshi
from crypto_monitor.analysis.spread_analyzer import SpreadAnalyzer
from crypto_monitor.analysis.volume_analyzer import VolumeAnalyzer

console = Console()

@click.command()
@click.option('--coin', default='BTC', help='Cryptocurrency symbol (e.g., BTC, XRP)')
@click.option('--interval', default=60, help='Update interval in seconds')
@click.option('--duration', default=10, help='How many intervals to run for')
@click.option('--display', default='rich', help='Display mode: rich or simple')

def monitor_price(coin: str, interval: int, duration: int, display: str):
    client = CoinspotClient()
    ha_analyzer = HeikinAshi()
    spread_analyzer = SpreadAnalyzer()
    volume_analyzer = VolumeAnalyzer()

    console.print(f"\n[bold blue]Monitoring {coin} price every {interval} seconds...[/bold blue]")

    for _ in range(duration):
        try:
            # Fetch and store price
            response = client.get_latest_price(coin)
            client.add_price_to_history(coin, response)

            # Fetch order book separately
            order_book = client.get_order_book(coin)

            # Get price history and calculate HA
            df = client.get_price_history(coin)
            if not df.empty:
                ha_df = ha_analyzer.calculate(df)
                ha_df = ha_analyzer.get_trend_signals(ha_df)
                spread_analysis = spread_analyzer.analyze_spread(df, coin)

                vbp_data = volume_analyzer.calculate_vbp(df)
                order_book_analysis = volume_analyzer.analyze_order_book(
                    order_book.get('buyorders', []),
                    order_book.get('sellorders', [])
                )
                
                volume_signals = volume_analyzer.get_volume_signals(
                    vbp_data,
                    order_book_analysis
                )

                # Get latest data point
                latest = ha_df.iloc[-1]
                latest_ha = ha_df.iloc[-1]

                if display == 'rich':
                    # Create rich table display
                    table = Table(title=f"{coin} Market Analysis")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value", style="green")

                    # Price Information
                    table.add_row("Timestamp", str(df.index[-1]))
                    table.add_row("Last Price", f"${latest['close']:,.2f}")
                    table.add_row("Bid Price", f"${latest['bid']:,.2f}")
                    table.add_row("Ask Price", f"${latest['ask']:,.2f}")

                    # Spread Information
                    table.add_row("", "")  # Empty row for spacing
                    table.add_row("[bold]Spread Analysis", "")
                    table.add_row("Current Spread", 
                                f"${latest['spread_absolute']:,.2f}")
                    table.add_row("Spread Percentage", 
                                f"{latest['spread_percentage']:.3f}%")

                    # Trend Information
                    table.add_row("", "")  # Empty row for spacing
                    table.add_row("[bold]Trend Analysis", "")
                    
                    trend_color = {
                        'bullish': 'green',
                        'bearish': 'red',
                        'neutral': 'yellow'
                    }.get(latest_ha['trend'].lower(), 'white')
                    
                    table.add_row("Heikin Ashi Trend", 
                                f"[{trend_color}]{latest_ha['trend'].upper()}[/{trend_color}]")

                    # Market Condition
                    condition_color = {
                        'TIGHT': 'green',
                        'NORMAL': 'yellow',
                        'WIDE': 'red'
                    }.get(spread_analysis['condition'], 'white')

                    table.add_row(
                        "Market Condition",
                        f"[{condition_color}]{spread_analysis['condition']}[/{condition_color}]"
                    )

                    # Market Message
                    table.add_row("", "")  # Empty row for spacing
                    message = get_market_message(latest_ha['trend'], spread_analysis['condition'])
                    table.add_row("[bold]Analysis", message)

                    # Volume Analysis
                    table.add_row("", "")
                    table.add_row("[bold]Volume Analysis", "")

                    imbalance_color = {
                        'buy': 'green',
                        'sell': 'red',
                        'neutral': 'yellow'
                    }.get(order_book_analysis['dominant_side'], 'white')

                    table.add_row(
                        "Order Book Imbalance",
                        f"[{imbalance_color}]{order_book_analysis['imbalance_ratio']:.2%}[/{imbalance_color}]"
                    )

                    if vbp_data.get('poc'):
                        table.add_row("Point of Control", vbp_data['poc'])
                    table.add_row("Volume Signals", volume_signals)
                    
                    console.clear()
                    console.print(table)

                else:
                    # Original simple display
                    click.echo(f"\nTimestamp: {df.index[-1]}")
                    click.echo(f"Price: ${latest['close']:,.2f}")
                    click.echo(f"Bid: ${latest['bid']:,.2f}")
                    click.echo(f"Ask: ${latest['ask']:,.2f}")
                    click.echo(f"Spread: ${spread_analysis['current_spread']:,.2f} "
                             f"({spread_analysis['current_spread_percentage']:.2f}%)")
                    click.echo(f"Trend: {latest['trend'].upper()}")
                    click.echo(f"Market Condition: {spread_analysis['condition']}")

            time.sleep(interval)

        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            import traceback
            traceback.print_exc()
            break

def get_market_message(trend: str, condition: str) -> str:
    ## Generate a market analysis message based on trend and condition
    messages = []
    
    if trend.lower() == 'bullish':
        messages.append("[green]Upward trend detected[/green]")
        if condition == 'TIGHT':
            messages.append("Good conditions for buying")
    elif trend.lower() == 'bearish':
        messages.append("[red]Downward trend detected[/red]")
        if condition == 'TIGHT':
            messages.append("Good conditions for selling")
    
    if condition == 'WIDE':
        messages.append("[red]Exercise caution - high spread[/red]")
    elif condition == 'TIGHT':
        messages.append("[green]Good liquidity conditions[/green]")
    
    return " • ".join(messages)

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