import questionary
from rich.console import Console
from rich.table import Table

from .game import Game


class MainMenuItems:
    LIST_PLAYERS = "List players"
    LIST_ROUNDS = "List rounds"
    QUIT = "Quit"


def main_menu(game: Game) -> None:
    while True:
        action = questionary.select(
            "What do you want to do?",
            choices=[
                MainMenuItems.LIST_PLAYERS,
                MainMenuItems.LIST_ROUNDS,
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
            case MainMenuItems.QUIT:
                save_menu()
                break
            case _:
                print("Invalid action")


def save_menu() -> None:
    want_to_save = questionary.confirm("Do you want to save your progress?").ask()
    if want_to_save:
        print("Saving progress...")
    else:
        print("Progress not saved")


def print_rounds(game: Game) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Round")
    for kind in game.trading.kinds:
        table.add_column(kind.name)

    for i, row in enumerate(game.rounds_price_list()):
        table.add_row(f"{i}", *[f"{price:.2f}" for price in row])

    console.print(table)
