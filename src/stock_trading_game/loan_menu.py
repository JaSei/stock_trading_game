from logging import Logger

import questionary
from rich.console import Console
from rich.table import Table

from .game import Game
from .model.loan import Loan


class LoanMenuItems:
    LIST_ACTIVE_LOANS = "List Active Loans"
    LIST_PLAYER_LOANS = "List player's loans"
    NEW_LOAN = "New Loan"
    PAY_LOAN = "Pay Loan"
    BACK = "Back to main menu"


def loan_menu(game: Game, log: Logger) -> None:
    while True:
        action = questionary.select(
            "What do you want to do?",
            choices=[
                LoanMenuItems.LIST_ACTIVE_LOANS,
                LoanMenuItems.LIST_PLAYER_LOANS,
                LoanMenuItems.NEW_LOAN,
                LoanMenuItems.PAY_LOAN,
                LoanMenuItems.BACK,
            ],
        ).ask()

        match action:
            case LoanMenuItems.LIST_ACTIVE_LOANS:
                list_active_loans(game)
            case LoanMenuItems.LIST_PLAYER_LOANS:
                list_player_loans(game)
            case LoanMenuItems.NEW_LOAN:
                new_loan(game, log)
            case LoanMenuItems.PAY_LOAN:
                pay_loan(game, log)
            case LoanMenuItems.BACK:
                break


def list_active_loans(game: Game) -> None:
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")

    table.add_column("Player")
    table.add_column("Amount")
    table.add_column("Interest Rate")
    table.add_column("Duration")
    table.add_column("Start Round")

    for player in game.players:
        for loan in player.loans:
            if loan.is_active():
                table.add_row(
                    player.name,
                    str(loan.amount),
                    str(loan.interest_rate),
                    str(loan.duration),
                    str(loan.start_round),
                )

    console.print(table)


def list_player_loans(game: Game) -> None:
    player_name = questionary.select(
        "Whose loans do you want to see?",
        choices=[player.name for player in game.players],
    ).ask()

    player = game.get_player_by_name(player_name)

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")

    table.add_column("Amount")
    table.add_column("Interest Rate")
    table.add_column("Duration")
    table.add_column("Start Round")

    for loan in player.loans:
        # inactives loans are striked through
        if loan.is_active():
            table.add_row(
                str(loan.amount),
                str(loan.interest_rate),
                str(loan.duration),
                str(loan.start_round),
            )
        else:
            table.add_row(
                f"[strikethrough]{loan.amount}[/strikethrough]",
                f"[strikethrough]{loan.interest_rate}[/strikethrough]",
                f"[strikethrough]{loan.duration}[/strikethrough]",
                f"[strikethrough]{loan.start_round}[/strikethrough]",
                style="strike",
            )

    console.print(table)


def new_loan(game: Game, log: Logger) -> None:
    player_name = questionary.select(
        "Who is taking the loan?",
        choices=[player.name for player in game.players],
    ).ask()

    player = game.get_player_by_name(player_name)

    amount = questionary.text(
        "How much do you want to borrow?",
        validate=lambda text: text.isdigit(),
    ).ask()

    interest_rate = questionary.text(
        "What is the interest rate in percent?",
        validate=lambda text: text.isdigit(),
        default="10",
    ).ask()

    duration = questionary.text(
        "What is the duration of the loan in rounds?",
        validate=lambda text: text.isdigit(),
        default="10",
    ).ask()

    loan = Loan(
        amount=int(amount),
        interest_rate=int(interest_rate),
        duration=int(duration),
        start_round=game.round,
    )

    print(
        f"{player_name} borrowed {amount} and will have to pay back {loan.final_amount()} in {duration} rounds."
    )

    agreement = questionary.confirm(
        "Do you agree to the terms?",
        default=False,
    ).ask()

    if agreement:
        log.info(
            f"{player_name} borrowed {amount} and will have to pay back {loan.final_amount()} in {duration} rounds."
        )

        player.take_loan(loan)


# return true if all loans are paid off
# return false if there are loans that are not paid off
def check_loans_are_paid(game: Game, log: Logger) -> bool:
    for player in game.players:
        for loan in player.loans:
            print(f"Checking loan of {player.name}")
            if loan.is_pay_off_round(game.round):
                print(f"{player.name} have to paid off the loan of {loan.final_amount()}")

                agreement = questionary.confirm(
                    "Do you able to pay off the loan?",
                    default=False,
                ).ask()

                if not agreement:
                    return False

                loan.pay_off()

                log.info(f"{player.name} paid off the loan of {loan.amount}")

    return True


def pay_loan(game: Game, log: Logger) -> None:
    list_active_loans(game)

    player_name = questionary.select(
        "Who is paying off the loan?",
        choices=[player.name for player in game.players],
    ).ask()

    player = game.get_player_by_name(player_name)

    loan_str = questionary.select(
        "Which active loan do you want to pay off?",
        choices=[
            f"{i}. {loan.final_amount()} in {loan.target_round()}"
            for i, loan in enumerate(player.loans)
            if loan.is_active()
        ],
    ).ask()

    loan_index = int(loan_str.split(".")[0])
    loan = player.loans[loan_index]

    agreement = questionary.confirm(
        f"Do you want to pay off {loan.final_amount()}?",
        default=False,
    ).ask()

    if agreement:
        loan.pay_off()

        log.info(f"{player_name} paid off the loan of {loan.amount}")
