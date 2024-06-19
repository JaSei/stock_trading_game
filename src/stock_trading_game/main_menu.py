import questionary

from .game import Game

class MainMenuItems:
    LIST_PLAYERS = "List players"
    QUIT = "Quit"

def main_menu(game: Game) -> None:
    while True:
        action = questionary.select(
            "What do you want to do?",
            choices=[MainMenuItems.LIST_PLAYERS, MainMenuItems.QUIT],
        ).ask()

        match action:
            case MainMenuItems.LIST_PLAYERS:
                print("Players:")
                for player in game.players:
                    print(player.name)
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
