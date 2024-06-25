import pytest
import os
import tempfile

from stock_trading_game.game import Game
from stock_trading_game.model.numerics import PercentChange, Price
from stock_trading_game.model.trading import Trading
from stock_trading_game.model.company import CompanyPlaceholder
from stock_trading_game.model.player import Player
from stock_trading_game.model.company import Company


@pytest.fixture
def game(trading: Trading) -> Game:
    return Game(players=[Player(name="Player 1"), Player(name="Player2")], trading=trading)


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

    assert game.rounds_price_list() == [
            [Price(10.0), Price(1000.0)],
            [Price(10.0), Price(1020.0)],
            [Price(10.1), Price(1020.0*1.03)],
            ]

    assert game.companies_list() == [
            [CompanyPlaceholder(), CompanyPlaceholder()],
            [CompanyPlaceholder(), CompanyPlaceholder()],
            [CompanyPlaceholder(), CompanyPlaceholder()],
            [CompanyPlaceholder(), None],
            [CompanyPlaceholder(), None],
            ]

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

def test_save_and_load(game: Game) -> None:
    game.shift_to_round(2)

    drevo = game.trading.kinds[0]
    players_share = {game.players[0]: 50, game.players[1]: 50}
    game.buy_company(drevo, "Company 1", players_share, Price(10))

    tmp_file = os.path.join(tempfile.gettempdir(), "test.json")
    game.save_to(tmp_file)

    game2 = game.load_from(tmp_file)

    assert game.round == game2.round
    assert game.rounds_price == game2.rounds_price
    assert game.companies == game2.companies
    assert game.trading.kinds == game2.trading.kinds
    assert game.trading.trends == game2.trading.trends
    assert game.companies == game2.companies
    assert game.players == game2.players
    assert game == game2
    assert game is not game2

def test_shift_company(game: Game) -> None:
    drevo = game.trading.kinds[0]
    players_share = {game.players[0]: 50, game.players[1]: 50}
    game.buy_company(drevo, "Company 1", players_share, Price(10))

    game.shift_to_next_round({drevo: PercentChange(0.1)})   

    company = game.companies[drevo][0]
    assert isinstance(company, Company)

    assert company.current_price() == Price(11)
    assert company.buy_round == 1
