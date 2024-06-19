from .game import Game
from .main_menu import main_menu
from .start_menu import start_menu


def main() -> None:
    players = start_menu()
    game = Game(players)
    main_menu(game)


if __name__ == "__main__":
    main()
