import pytest

from stock_trading_game.game import Game
from stock_trading_game.numerics import PercentChange, Price
from stock_trading_game.trading import Trading


@pytest.fixture
def game(trading: Trading) -> Game:
    return Game(players=[], trading=trading)


def test_next_round_and_shift(game: Game) -> None:
    drevo = game.trading.kinds[0]
    zlato = game.trading.kinds[1]

    assert game.round == 0
    assert game.next_round() == 1

    assert game.current_round_price(drevo) == Price(10)
    assert game.next_round_kind_trend(drevo) == PercentChange(0.00)

    assert game.current_round_price(zlato) == Price(1000)
    assert game.next_round_kind_trend(zlato) == PercentChange(0.02)

    game.shift_to_next_round()

    assert game.round == 1
    assert game.next_round() == 2

    drevo_first_round_price = Price(10.0)
    assert game.current_round_price(drevo) == drevo_first_round_price

    zlato_first_round_price = Price(1020.0)
    assert game.current_round_price(zlato) == zlato_first_round_price

    game.shift_to_next_round()

    assert game.round == 2
    assert game.next_round() == 3

    assert game.current_round_price(drevo) == drevo_first_round_price * 1.01
    assert game.current_round_price(zlato) == zlato_first_round_price * 1.03


def test_next_round_and_shift_with_extra(game: Game) -> None:
    drevo = game.trading.kinds[0]
    zlato = game.trading.kinds[1]

    assert game.round == 0
    assert game.next_round() == 1

    assert game.current_round_price(drevo) == Price(10)
    assert game.next_round_kind_trend(drevo) == PercentChange(0.00)

    assert game.current_round_price(zlato) == Price(1000)
    assert game.next_round_kind_trend(zlato) == PercentChange(0.02)

    game.shift_to_next_round({drevo: PercentChange(0.1)})

    assert game.round == 1
    assert game.next_round() == 2

    drevo_first_round_price = Price(11.0)
    assert game.current_round_price(drevo) == drevo_first_round_price

    zlato_first_round_price = Price(1020.0)
    assert game.current_round_price(zlato) == zlato_first_round_price

    game.shift_to_next_round({zlato: PercentChange(0.1)})

    assert game.round == 2
    assert game.next_round() == 3

    assert pytest.approx(game.current_round_price(drevo)) == drevo_first_round_price * 1.01
    assert pytest.approx(game.current_round_price(zlato)) == zlato_first_round_price * 1.13


def test_shift_to_round(game: Game) -> None:
    drevo = game.trading.kinds[0]
    zlato = game.trading.kinds[1]

    game.shift_to_round(2)

    assert game.round == 2
    assert game.next_round() == 3

    assert game.current_round_price(drevo) == Price(10.0) * 1.01
    assert game.current_round_price(zlato) == Price(1020.0) * 1.03
