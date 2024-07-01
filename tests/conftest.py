import pytest
from logging import Logger

from stock_trading_game.game import Game
from stock_trading_game.model.trading import Trading
from stock_trading_game.start_menu import parse_trading_csv
from stock_trading_game.model.player import Player
from stock_trading_game.model.trading import Trading


@pytest.fixture
def trading() -> Trading:
    path = "tests/trading_data.csv"
    return parse_trading_csv(path)


@pytest.fixture
def game(trading: Trading) -> Game:
    return Game(players=[Player(name="Player 1"), Player(name="Player2")], trading=trading)


@pytest.fixture
def log() -> Logger:
    return Logger("test")
