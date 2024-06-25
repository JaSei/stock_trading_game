from datetime import datetime
import traceback
import os

import questionary
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from .game import Game
from .model.numerics import format_price, PercentChange, Price
from .model.shares import AMOUNT_OF_SHARES
from .model.company import Company


class MainMenuItems:
    LIST_PLAYERS = "List players"
    LIST_ROUNDS = "List rounds"
    LIST_COMPANIES_HISTORY = "List companies history"
    LIST_COMPANIES = "List companies"
    BUY_COMPANY = "Buy company"
    SHARE_TRADE = "Share trade"
    LIST_SHAREHOLDERS = "List shareholders"
    NEXT_ROUND = "Next round"
    QUIT = "Quit"


def main_menu(game: Game) -> None:
    while True:
        try:
            action = questionary.select(
                "What do you want to do?",
                choices=[
                    MainMenuItems.LIST_PLAYERS,
                    MainMenuItems.LIST_ROUNDS,
                    MainMenuItems.LIST_COMPANIES_HISTORY,
                    MainMenuItems.LIST_COMPANIES,
                    MainMenuItems.BUY_COMPANY,
                    MainMenuItems.SHARE_TRADE,
                    MainMenuItems.LIST_SHAREHOLDERS,
                    MainMenuItems.NEXT_ROUND,
                    MainMenuItems.QUIT,
                ],
            ).ask()

            match action:
                case MainMenuItems.LIST_PLAYERS:
                    print("Players:")
                    for player in game.players:
                        print(player.name)
                case MainMenuItems.LIST_ROUNDS:
                    print_rounds(game)
                case MainMenuItems.LIST_COMPANIES_HISTORY:
                    print_companies_history(game)
                case MainMenuItems.LIST_COMPANIES:
                    print_companies(game)
                case MainMenuItems.BUY_COMPANY:
                    buy_company(game)
                case MainMenuItems.SHARE_TRADE:
                    share_trade(game)
                case MainMenuItems.LIST_SHAREHOLDERS:
                    print_shareholders(game)
                case MainMenuItems.NEXT_ROUND:
                    next_round(game)
                case MainMenuItems.QUIT:
                    save_menu(game)
                    break
                case _:
                    print("Invalid action")
        except Exception:  # pylint: disable=broad-except
            print(traceback.format_exc())


def save_menu(game: Game) -> None:
    want_to_save = questionary.confirm("Do you want to save your progress?").ask()
    if want_to_save:
        while True:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file = questionary.path(
                "Enter the name of the save file",
                default=f"{now}.json",
                validate=lambda path: path.endswith(".json")
                or "Invalid path, must end with .json",
            ).ask()

            if os.path.exists(file):
                overwrite = questionary.confirm(
                    "File already exists, do you want to overwrite it?"
                ).ask()
                if overwrite:
                    break
            else:
                break

        game.save_to(file)
    else:
        print("Progress not saved")


def print_rounds(game: Game, from_i: int = 0) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Round")
    for kind in game.trading.kinds:
        table.add_column(kind.name)

    previous_prices: list[Price] = []
    for i, row in enumerate(game.rounds_price_list()):
        if i < from_i:
            continue

        kinds_value_row = []
        for j, price in enumerate(row):
            try:
                prev_price = previous_prices[j]
                percent_change = round((price - prev_price) / prev_price * 100, 2)

                if percent_change > 0:
                    percent_change_string = f"[green]{percent_change:.2f}%[/green]"
                elif percent_change < 0:
                    percent_change_string = f"[red]{percent_change:.2f}%[/red]"
                else:
                    percent_change_string = f"{percent_change:.2f}%"
            except IndexError:
                percent_change_string = "-"

            kinds_value_row.append(f"{format_price(price)} ({percent_change_string})")

        previous_prices = row
        table.add_row(f"{i}", *kinds_value_row)

    console.print(table)


def print_companies_history(game: Game) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Round")
    for company in game.tradable_companies():
        table.add_column(company.name)

    for i in range(game.round+1):
        row = [f"{i}"]
        for company in game.tradable_companies():
            if i < company.buy_round:
                row.append("-")
            else:
                try:
                    round_id = i - company.buy_round
                    price = company.prices[round_id]
                    prev_price = company.prices[round_id - 1]
                    percent_change = round((price - prev_price) / prev_price * 100, 2)

                    if percent_change > 0:
                        percent_change_string = f"[green]{percent_change:.2f}%[/green]"
                    elif percent_change < 0:
                        percent_change_string = f"[red]{percent_change:.2f}%[/red]"
                    else:
                        percent_change_string = f"{percent_change:.2f}%"
                except (IndexError, ZeroDivisionError):
                    price = Price(0)
                    percent_change_string = "-"

                row.append(f"{format_price(price)} ({percent_change_string})")

        table.add_row(*row)

    console.print(table)

def print_companies(game: Game) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    for kind in game.trading.kinds:
        table.add_column(kind.name)

    for row in game.companies_list():
        table.add_row(*[str(company) for company in row])

    console.print(table)


def buy_company(game: Game) -> None:
    print("Buying a company...")

    kind = questionary.select(
        "Which company kind do you want to buy?",
        choices=[kind.name for kind in game.get_free_company_kinds()],
    ).ask()

    name = questionary.text(
        "Enter the name of the company",
        validate=lambda name: game.validate_company_name(name),
    ).ask()

    players_name = questionary.checkbox(
        "Which player(s) is buying?",
        choices=[player.name for player in game.players],
        validate=lambda players: len(players) > 0 or "Select at least one player",
    ).ask()

    players = [
        next(filter(lambda player: player.name == name, game.players)) for name in players_name
    ]

    price = questionary.text(
        "Enter the price",
        validate=lambda price: price.lstrip("-").isdigit() or "Invalid price",
    ).ask()

    while True:
        shares: list[int] = []
        for player in players:
            share = questionary.text(
                f"Enter the number of shares for {player}",
                validate=lambda share: share.lstrip("-").isdigit() or "Invalid share",
            ).ask()
            shares.append(int(share))

        if sum_of_shares := sum(shares) != AMOUNT_OF_SHARES:
            print(f"Sum of shares must be {AMOUNT_OF_SHARES}, not {sum_of_shares}")
        else:
            break

    players_share = dict(zip(players, shares))

    game.buy_company(game.company_kind_by_name(kind), name, players_share, price)


def share_trade(game: Game) -> None:
    print("Share trading...")

    company_name = questionary.select(
        "Which company do you want to trade?",
        choices=[company.name for company in game.tradable_companies()],
    ).ask()

    print(f"Trading {company_name}...")

    company = game.company_by_name(company_name)

    from_player_name = questionary.select(
        "Which player is trading?",
        choices=[player.name for player in company.owners()],
    ).ask()

    from_player = next(filter(lambda player: player.name == from_player_name, game.players))

    to_player_name = questionary.select(
        "Which player is receiving?",
        choices=[player.name for player in game.players],
    ).ask()

    to_player = next(filter(lambda player: player.name == to_player_name, game.players))

    amount = questionary.text(
        "Enter the number of shares to trade",
        validate=lambda amount: company.validate_player_share(from_player, amount),
    ).ask()

    company.trade_shares(from_player, to_player, int(amount))


def print_shareholders(game: Game) -> None:
    console = Console()

    tree = Tree("Shareholders")
    for company_kind in game.companies:
        company_kind_node = tree.add(company_kind.name)
        for company in game.companies[company_kind]:
            if isinstance(company, Company):
                company_node = company_kind_node.add(
                    f"{company.name} ({format_price(company.current_price())})"
                )
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Player")
                table.add_column("Share")
                table.add_column("Price")

                for player in company.owners():
                    table.add_row(
                        player.name,
                        str(company.owner_amount_of_shares(player)),
                        format_price(company.owner_shares_value(player)),
                    )

                company_node.add(table)

    console.print(tree)


def next_round(game: Game) -> None:
    print(f"Shifting from {game.round} to next round {game.next_round()}...")

    print_rounds(game, game.round-1)

    extra_percent_change = {}
    for kind in game.companies:
        extra = questionary.text(
            f"Extra percent change trend for {kind.name}",
            default="0",
            validate=lambda extra: extra.lstrip("-").isdigit() or "Invalid trend",
        ).ask()
        extra_percent_change[kind] = PercentChange(float(extra) / 100)

    game.shift_to_next_round(extra_percent_change)

    print_rounds(game, game.round-1)
