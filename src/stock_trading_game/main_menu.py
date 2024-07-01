import logging
import math
import os
import traceback
from datetime import datetime
from typing import Optional

import questionary
from rich.console import Console
from rich.table import Table

from .dividends_menu import check_dividends, dividends_menu
from .game import Game
from .loan_menu import check_loans_are_paid, list_active_loans, loan_menu
from .model.numerics import (
    OneSharePrice,
    PercentChange,
    Price,
    TotalPrice,
    format_price,
)
from .model.player import Player
from .model.shares import AMOUNT_OF_SHARES
from .print.shareholders import print_shareholders
from .validators import validate_float, validate_minimal_price


class MainMenuItems:
    LIST_PLAYERS = "List players"
    LIST_ROUNDS = "List rounds"
    LIST_COMPANIES_HISTORY = "List companies history"
    LIST_COMPANIES = "List companies"
    BUY_COMPANY = "Buy company"
    EXTEND_COMPANY = "Extend company"
    SHARE_TRADE = "Share trade"
    BUY_SHARES_FROM_BANK = "Buy shares from bank"
    LIST_SHAREHOLDERS = "List shareholders"
    NEXT_ROUND = "Next round"
    LOAN_MENU = "Loan"
    LIST_SHARES_BY_PLAYER = "List shares by player"
    DIVIDENDS = "Dividends"
    QUIT = "Quit"


def main_menu(game: Game) -> None:
    log = logging.getLogger(__name__)

    while True:
        try:
            console = Console()
            console.print(f"Round: {game.round}", style="bold")

            action = questionary.select(
                "What do you want to do?",
                choices=[
                    MainMenuItems.BUY_SHARES_FROM_BANK,
                    MainMenuItems.LIST_SHAREHOLDERS,
                    MainMenuItems.LIST_COMPANIES_HISTORY,
                    MainMenuItems.LIST_COMPANIES,
                    MainMenuItems.SHARE_TRADE,
                    MainMenuItems.BUY_COMPANY,
                    MainMenuItems.EXTEND_COMPANY,
                    MainMenuItems.NEXT_ROUND,
                    MainMenuItems.LOAN_MENU,
                    MainMenuItems.DIVIDENDS,
                    MainMenuItems.LIST_ROUNDS,
                    MainMenuItems.LIST_SHARES_BY_PLAYER,
                    MainMenuItems.LIST_PLAYERS,
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
                    buy_company(game, log)
                case MainMenuItems.EXTEND_COMPANY:
                    extend_company(game, log)
                case MainMenuItems.SHARE_TRADE:
                    share_trade(game, log)
                case MainMenuItems.BUY_SHARES_FROM_BANK:
                    buy_share_from_bank(game, log)
                case MainMenuItems.LIST_SHAREHOLDERS:
                    print_shareholders(game)
                case MainMenuItems.NEXT_ROUND:
                    if check_loans_are_paid(game, log):
                        next_round(game, log)
                        check_dividends(game, log)
                        list_active_loans(game)
                    else:
                        print("Loans are not paid")
                case MainMenuItems.LOAN_MENU:
                    loan_menu(game, log)
                case MainMenuItems.LIST_SHARES_BY_PLAYER:
                    list_shares_by_player(game)
                case MainMenuItems.DIVIDENDS:
                    dividends_menu(game, log)
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

    previous_prices: list[TotalPrice] = []
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

    for game_round in range(game.round + 1):
        row = [f"{game_round}"]

        for company in game.tradable_companies():
            extension = ""
            if company.has_built_extension(game_round):
                extension = "🏢"

            if game_round < company.buy_round:
                row.append("-")
            else:
                try:
                    price_id = game_round - company.buy_round
                    if price_id == 0:
                        price = company.prices[0]
                        percent_change_string = "-"
                    else:
                        price = company.prices[price_id]
                        prev_price = company.prices[price_id - 1]
                        percent_change = round((price - prev_price) / prev_price * 100, 2)

                        if percent_change > 0:
                            percent_change_string = f"[green]{percent_change:.2f}%[/green]"
                        elif percent_change < 0:
                            percent_change_string = f"[red]{percent_change:.2f}%[/red]"
                        else:
                            percent_change_string = f"{percent_change:.2f}%"
                except (IndexError, ZeroDivisionError):
                    price = TotalPrice(0)
                    percent_change_string = "-"

                row.append(f"{format_price(price)} ({percent_change_string}) {extension}")

        table.add_row(*row)

    console.print(table)


def print_companies(game: Game) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    for kind in game.trading.kinds:
        table.add_column(
            f"{kind.name} (trend:{format_price(game.current_round_price(kind))}, avg:{format_price(game.average_price(kind))})"
        )

    for row in game.companies_list():
        table.add_row(*[str(company) for company in row])

    console.print(table)


def buy_company(game: Game, log: logging.Logger) -> None:
    print("Buying a company...")

    print_companies(game)

    kind_name = questionary.select(
        "Which company kind do you want to buy?",
        choices=[kind.name for kind in game.get_free_company_kinds()],
    ).ask()

    kind = game.company_kind_by_name(kind_name)

    log.info("Buying a company of kind %s", kind)

    name = questionary.text(
        "Enter the name of the company",
        validate=lambda name: game.validate_company_name(name),
        placeholder="Company name",
    ).ask()

    log.info("Company name: %s", name)

    players_name = questionary.checkbox(
        "Which player(s) is buying?",
        choices=[player.name for player in game.players],
        validate=lambda players: len(players) > 0 or "Select at least one player",
    ).ask()

    log.info("Players buying: %s", players_name)

    players = [game.get_player_by_name(player_name) for player_name in players_name]

    price = TotalPrice(
        float(
            questionary.text(
                "Enter the price",
                validate=lambda price: validate_minimal_price(game, kind, price),
                placeholder="Initial company price",
            ).ask()
        )
    )

    log.info("Price: %s", price)

    while True:
        shares: list[int] = []
        for player in players:
            share = questionary.text(
                f"Enter the number of shares for {player.name}",
                validate=lambda share: share.lstrip("-").isdigit() or "Invalid share",
            ).ask()
            shares.append(int(share))

        if sum_of_shares := sum(shares) != AMOUNT_OF_SHARES:
            print(f"Sum of shares must be {AMOUNT_OF_SHARES}, not {sum_of_shares}")
        else:
            break

    players_share = dict(zip(players, shares))

    log.info("Players share: %s", players_share)

    game.buy_company(kind, name, players_share, price)


def extend_company(game: Game, log: logging.Logger) -> None:
    print("Extending a company...")

    company_name = questionary.select(
        "Which company do you want to extend?",
        choices=[company.name for company in game.tradable_companies()],
    ).ask()

    company = game.company_by_name(company_name)

    list_shares_by_player(game, game.bank())

    extension_price = questionary.text(
        "Enter the price for extending",
        validate=lambda price: price.isdigit() or "Invalid price",
    ).ask()

    log.info("Company '%s' extending with price %s", company_name, extension_price)

    company.extend(game.round, Price(float(extension_price)))

    print_shareholders(game, company)


def share_trade(game: Game, log: logging.Logger) -> None:
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

    from_player = game.get_player_by_name(from_player_name)

    to_player_name = questionary.select(
        "Which player is receiving?",
        choices=[player.name for player in game.players],
    ).ask()

    to_player = game.get_player_by_name(to_player_name)

    amount = int(
        questionary.text(
            "Enter the number of shares to trade",
            validate=lambda amount: company.validate_player_share(from_player, amount),
        ).ask()
    )

    price = TotalPrice(
        float(
            questionary.text(
                "Enter the price for trading shares",
                validate=lambda price: validate_float(price),
                default=str(company.current_one_share_price() * amount),
            ).ask()
        )
    )

    company.trade_shares(log, from_player, to_player, int(amount), OneSharePrice(price / amount))


def buy_share_from_bank(game: Game, log: logging.Logger) -> None:
    print("Buying shares from bank...")

    list_shares_by_player(game, game.bank())

    company_name = questionary.select(
        "Which company do you want to buy shares from?",
        choices=[company.name for company in game.bank_companies()],
    ).ask()

    company = game.company_by_name(company_name)

    print(f"Buying shares from {company_name}...")

    investment = Price(
        float(
            questionary.text(
                "How much money do you want to invest?",
                validate=lambda money: validate_float(money),
            ).ask()
        )
    )

    maximum_shares_to_buy = int(investment / company.current_one_share_price())

    print(f"Maximum shares to buy: {maximum_shares_to_buy}")

    contiune = questionary.confirm("Do you want to continue?").ask()

    if not contiune:
        return

    approved_shares = int(
        questionary.text(
            "Enter the number of shares to buy",
            validate=lambda amount: amount.isdigit() and 0 < int(amount) <= maximum_shares_to_buy,
            default=str(maximum_shares_to_buy),
        ).ask()
    )

    price = Price(company.current_one_share_price() * approved_shares)
    rounded_price = Price(math.ceil(price))

    print(
        f"Approved shares: {approved_shares}, price: {format_price(rounded_price)} ({format_price(price)})"
    )

    player_name = questionary.select(
        "Which player is buying?",
        choices=[player.name for player in game.players],
    ).ask()

    player = game.get_player_by_name(player_name)

    company.trade_shares(
        log, game.bank(), player, approved_shares, OneSharePrice(rounded_price / approved_shares)
    )


def next_round(game: Game, log: logging.Logger) -> None:
    print(f"Shifting from {game.round} to next round {game.next_round()}...")
    log.info("Shifting from %s to next round %s", game.round, game.next_round())

    print_rounds(game, game.round - 1)

    extra_percent_change = {}
    for kind in game.companies:
        extra = questionary.text(
            f"Extra percent change trend for {kind.name}",
            default="0",
            validate=lambda extra: extra.lstrip("-").isdigit() or "Invalid trend",
        ).ask()
        extra_percent_change[kind] = PercentChange(float(extra) / 100)

    log.info("Extra percent change: %s", extra_percent_change)

    game.shift_to_next_round(extra_percent_change)

    print_rounds(game, game.round - 1)


def list_shares_by_player(game: Game, player: Optional[Player] = None) -> None:
    if player is None:
        player_name = questionary.select(
            "Which player do you want to list shares?",
            choices=[player.name for player in game.players],
        ).ask()

        player = game.get_player_by_name(player_name)

    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Company")
    table.add_column("Share")
    table.add_column("Share price")

    for company in game.tradable_companies():
        try:
            share = company.owner_amount_of_shares(player)
            share_price = company.current_one_share_price()

            table.add_row(company.name, str(share), format_price(share_price))
        except KeyError:
            pass

    console.print(table)
