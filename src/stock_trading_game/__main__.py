from .main_menu import main_menu
from .start_menu import start_menu


def main() -> None:
    game = start_menu()
    main_menu(game)


if __name__ == "__main__":
    main()
