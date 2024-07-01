from .game import Game
from .model.company_kind import CompanyKind
from .model.numerics import format_price

def validate_float(value: str) -> str | bool:
    try:
        float(value)
    except ValueError:
        return "Not a number"
    return True

def validate_minimal_price(game: Game, kind: CompanyKind, text: str) -> str | bool:
    try:
        price = float(text)
    except ValueError:
        return "Invalid price"

    current_round_price = game.current_round_price(kind)

    if price < current_round_price:
        return f"Price must be at least {format_price(current_round_price)}"

    return True

