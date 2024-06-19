import csv
import sys

import questionary

from .company_kind import CompanyKind, CompanyKindTrend
from .player import Player
from .trading import Trading
from .game import Game


class StartMenuItems:
    NEW_GAME = "Start a new game"
    LOAD_GAME = "Load a saved game"
    QUIT = "Quit"


def start_menu() -> Game:
    print("Welcome to the Stock Trading Game!")

    action = questionary.select(
        "What do you want to do?",
        choices=[StartMenuItems.NEW_GAME, StartMenuItems.LOAD_GAME, StartMenuItems.QUIT],
    ).ask()

    players = list[Player]()
    trading = Trading(kinds=[], trends=[])
    initial_round = 0
    match action:
        case StartMenuItems.NEW_GAME:
            print("Starting a new game...")
            players_text = questionary.text(
                "Players:",
                multiline=True,
                instruction="Enter each player on a new line, end with esc and enter",
            ).ask()
            players = [Player(name=player) for player in players_text.split("\n")]

            read_csv = True
            while read_csv:
                path = questionary.path(
                    "Enter the path to trading csv data",
                    validate=lambda path: path.endswith(".csv")
                    or "Invalid path, must end with .csv",
                ).ask()

                trading = parse_trading_csv(path)

                trading.print_summary()

                read_csv = not questionary.confirm("Is this the correct data?").ask()

            initial_round = int(questionary.text(
                "Enter the initial round number",
                default="0",
                validate=lambda round: (round.isdigit() and int(round) < trading.max_rounds()) or "Invalid round number",
            ).ask())

        case StartMenuItems.LOAD_GAME:
            print("Loading a saved game...")
        case StartMenuItems.QUIT:
            print("Quitting...")
            sys.exit(0)
        case _:
            print("Invalid action")

    game = Game(players=players, trading=trading)
    game.shift_to_round(initial_round)

    return game


# first column is only metadata, it can be skipped
# first row is CompanyKind
# second row means amount of companies in the CompanyKind
# third row is initial CompanyKind price in round 0
# fourth row and rest are CompanyKindTrend (percentage change in double format)
def parse_trading_csv(path: str) -> Trading:
    print(f"Parsing trading data from {path}...")

    company_kinds = []
    with open(path) as file:
        reader = csv.reader(file)
        company_kind = next(reader)[1:]
        company_kind_amount = list(map(int, next(reader)[1:]))
        company_kind_price = list(map(float, next(reader)[1:]))

        for i in range(len(company_kind)):
            kind = CompanyKind(
                name=company_kind[i],
                amount=company_kind_amount[i],
                initial_price=company_kind_price[i],
            )
            company_kinds.append(kind)

        trend_data: list[CompanyKindTrend] = []
        for i, kind in enumerate(company_kinds):
            trend_data.append(CompanyKindTrend(trend=[]))

        for row in reader:
            for i, value in enumerate(row[1:]):
                trend_data[i].add_trend(float(value.replace(",", ".")))

    return Trading(kinds=company_kinds, trends=trend_data)
