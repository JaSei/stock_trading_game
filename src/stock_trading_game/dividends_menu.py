from logging import Logger

import questionary
from rich.table import Table
from rich.console import Console

from .game import Game
from .print.shareholders import print_shareholders
from .model.numerics import format_price, Price


class DividendsMenu:
    SET_DIVIDENDS = "Set Dividends"
    REMOVE_DIVIDENDS = "Remove Dividends"
    VIEW_COMPANY_DIVIDENDS = "View Company Dividends"
    EXIT = "Exit"


def dividends_menu(game: Game, log: Logger) -> None:
    while True:
        choice = questionary.select(
            "What do you want to do?",
            choices=[
                DividendsMenu.SET_DIVIDENDS,
                DividendsMenu.REMOVE_DIVIDENDS,
                DividendsMenu.VIEW_COMPANY_DIVIDENDS,
                DividendsMenu.EXIT,
            ],
        ).ask()

        match choice:
            case DividendsMenu.SET_DIVIDENDS:
                set_dividends(game, log)
            case DividendsMenu.REMOVE_DIVIDENDS:
                print("Remove Dividends")
            case DividendsMenu.VIEW_COMPANY_DIVIDENDS:
                view_company_dividends(game)
            case DividendsMenu.EXIT:
                break


def set_dividends(game: Game, log: Logger) -> None:
    print("Set Dividends")

    company_name = questionary.select(
        "Which company do you want to set dividends for?",
        choices=[company.name for company in game.list_companies_without_dividents()],
    ).ask()

    company = game.company_by_name(company_name)

    dividend_period = questionary.text(
        "How often do you want to pay dividends?",
        validate=lambda text: text.isdigit() and int(text) > 0,
        default="10",
    ).ask()

    log.info(f"Set dividends for {company_name} every {dividend_period} rounds")

    company.set_dividends(game.round, int(dividend_period))


def remove_dividends(game: Game) -> None:
    print("Remove Dividends")

    company_name = questionary.select(
        "Which company do you want to remove dividends for?",
        choices=[company.name for company in game.list_companies_without_dividents()],
    ).ask()

    company = game.company_by_name(company_name)

    company.disable_dividends()


def view_company_dividends(game: Game) -> None:
    print("View Company Dividends")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Company", style="dim", width=12)
    table.add_column("Dividends period", justify="right")
    table.add_column("Next divident round", justify="right")
    table.add_column("Rounds left", justify="right")

    for company in game.tradable_companies():
        if company.is_dividend_active():
            next_round = company.next_dividend_round()
            table.add_row(
                company.name,
                str(company.dividend_period),
                str(next_round),
                str(next_round - game.round),
            )
        else:
            table.add_row(company.name, "-", "-")

    console = Console()
    console.print(table)


def check_dividends(game: Game, log: Logger) -> None:
    for company in game.list_companies_with_dividends():
        if company.is_dividend_round(game.round):
            while True:
                print(f"{company.name} paid dividends")
                print_shareholders(game, company)

                dividend_to_pay = questionary.text(
                    "How much do you want to pay in dividends to all shareholders?",
                    validate=lambda text: text.isdigit() and int(text) >= 0,
                ).ask()

                console = Console()
                table = Table(show_header=True, header_style="bold magenta")

                table.add_column("Player", style="dim", width=12)
                table.add_column("Shares", justify="right")
                table.add_column("Dividends", justify="right")

                for player in company.owners():
                    shares_abs = company.owner_amount_of_shares(player)
                    shares_percent = company.owner_percent_share(player)
                    table.add_row(
                        player.name,
                        str(shares_abs),
                        format_price(Price(int(dividend_to_pay) * shares_percent)),
                    )
                console.print(table)

                aggrees = questionary.confirm(
                    "Do you agree with the dividends?", default=False
                ).ask()
                if aggrees:
                    company.divident_paid(game.round, int(dividend_to_pay))
                    log.info(f"{company.name} paid {dividend_to_pay} in dividends")
                    for player in company.owners():
                        log.info(
                            f"{player.name} got {int(dividend_to_pay) / company.owner_amount_of_shares(player)} in dividends"
                        )
                    break
