from logging import Logger

import questionary
from rich.console import Console
from rich.table import Table

from .game import Game
from .model.trading import Trading, parse_trading_csv


class GameMenuItems:
    RELOAD_TREND = "Reload Trend"
    EXPORT_ROUND_PRICES = "Export Round Prices"
    BACK = "Back to main menu"


def game_menu(game: Game, log: Logger) -> None:
    while True:
        action = questionary.select(
            "What do you want to do?",
            choices=[
                GameMenuItems.RELOAD_TREND,
                GameMenuItems.EXPORT_ROUND_PRICES,
                GameMenuItems.BACK,
            ],
        ).ask()

        match action:
            case GameMenuItems.RELOAD_TREND:
                reload_trend(game, log)
            case GameMenuItems.EXPORT_ROUND_PRICES:
                export_round_prices(game, log)
            case GameMenuItems.BACK:
                break


def reload_trend(game: Game, log: Logger) -> None:
    log.info("Reloading trend")

    path = questionary.path(
        "Enter the path to new trading csv data",
        validate=lambda path: path.endswith(".csv") or "Invalid path, must end with .csv",
    ).ask()

    trading = parse_trading_csv(path)

    trading.print_summary()

    correct_data = questionary.confirm(
        "Is this the correct data?",
        default=False,
    ).ask()

    if not correct_data:
        return

    _compare_trend_and_print_diff(game.trading, trading)

    really_reload = questionary.confirm("Do you want to reload the trend?").ask()

    if really_reload:
        print("Reloading trend...")
        log.info("Reloading trend from %s", path)
        game.trading.trends = trading.trends
    else:
        print("Noting changed, trend not reloaded")


def _compare_trend_and_print_diff(current_trend: Trading, new_trend: Trading) -> None:
    if current_trend.max_rounds() > new_trend.max_rounds():
        raise ValueError("New trend has less rounds")

    for i in range(len(current_trend.kinds)):
        if current_trend.kinds[i] != new_trend.kinds[i]:
            raise ValueError("Trading data has different company kinds")

    console = Console()
    table = Table(title="Trend comparison")
    table.add_column("Round", justify="right")
    for kind in current_trend.kinds:
        table.add_column(kind.name, justify="right")

    for i in range(new_trend.max_rounds()):
        row = [str(i)]
        for j in range(len(new_trend.kinds)):
            if i >= len(current_trend.trends[j].trend):
                current = "N/A"
            else:
                current = str(current_trend.trends[j].trend[i])
            new = str(new_trend.trends[j].trend[i])

            if current == new:
                row.append(f"[green]{current} = {new}[/green]")
            else:
                row.append(f"[red]{current} != {new}[/red]")

        table.add_row(*row)

    console.print(table)


def export_round_prices(game: Game, log: Logger) -> None:
    path = questionary.path(
        "Enter the path to export the round prices to",
        validate=lambda path: path.endswith(".csv") or "Invalid path, must end with .csv",
    ).ask()

    game.export_round_prices_to_csv(path)
    log.info("Exported round prices to %s", path)
    print(f"Exported round prices to {path}")
