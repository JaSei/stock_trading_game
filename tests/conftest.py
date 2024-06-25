import pytest

from stock_trading_game.model.trading import Trading
from stock_trading_game.start_menu import parse_trading_csv

@pytest.fixture
def trading() -> Trading:
    path = "tests/trading_data.csv"
    return parse_trading_csv(path)
