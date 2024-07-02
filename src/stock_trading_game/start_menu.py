import sys
import logging

import questionary

from .game import Game
from .model.player import Player
from .model.trading import Trading
from .model.trading import parse_trading_csv


class StartMenuItems:
    NEW_GAME = "Start a new game"
    LOAD_GAME = "Load a saved game"
    QUIT = "Quit"


def start_menu() -> Game:
    print("Welcome to the Stock Trading Game!")

    log = logging.getLogger(__name__)

    action = questionary.select(
        "What do you want to do?",
        choices=[StartMenuItems.NEW_GAME, StartMenuItems.LOAD_GAME, StartMenuItems.QUIT],
    ).ask()

    game = None
    match action:
        case StartMenuItems.NEW_GAME:
            players = list[Player]()
            trading = Trading(kinds=[], trends=[])
            initial_round = 0

            print("Starting a new game...")
            log.info("Starting a new game...")
            players_text = questionary.text(
                "Players:",
                multiline=True,
                instruction="Enter each player on a new line, end with esc and enter",
            ).ask()
            players = [Player(name=player) for player in players_text.split("\n")]
            players.append(Player(name="Bank"))

            log.info("Players: %s", players_text)

            read_csv = True
            while read_csv:
                path = questionary.path(
                    "Enter the path to trading csv data",
                    validate=lambda path: path.endswith(".csv")
                    or "Invalid path, must end with .csv",
                ).ask()

                log.info("Trading data path: %s", path)

                trading = parse_trading_csv(path)

                trading.print_summary()

                read_csv = not questionary.confirm("Is this the correct data?").ask()

            initial_round = int(
                questionary.text(
                    "Enter the initial round number",
                    default="0",
                    validate=lambda round: (round.isdigit() and int(round) < trading.max_rounds())
                    or "Invalid round number",
                ).ask()
            )

            log.info("Initial round: %s", initial_round)

            game = Game(players=players, trading=trading)
            game.shift_to_round(initial_round)

        case StartMenuItems.LOAD_GAME:
            print("Loading a saved game...")
            log.info("Loading a saved game...")
            file_path = questionary.path(
                "Enter the path to the saved game",
                validate=lambda path: path.endswith(".json")
                or "Invalid path, must end with .json",
            ).ask()

            log.info("Saved game path: %s", file_path)

            game = Game.load_from(file_path)

        case StartMenuItems.QUIT:
            print("Quitting...")
            sys.exit(0)
        case _:
            print("Invalid action")

    assert game is not None

    return game



