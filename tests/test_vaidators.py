from stock_trading_game.validators import validate_minimal_price
from stock_trading_game.game import Game

def test_validate_minimal_price(game: Game) -> None:
    drevo = game.trading.kinds[0]

    assert validate_minimal_price(game, drevo, "0.0") == "Price must be at least $10.0"
