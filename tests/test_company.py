from logging import Logger

import pytest

from stock_trading_game.model.company import Company
from stock_trading_game.model.numerics import OneSharePrice, Price, TotalPrice
from stock_trading_game.model.player import Player
from stock_trading_game.model.shares import Shares


def test_company(log: Logger) -> None:
    shares = Shares(
        players_share={
            Player(name="Player 1"): 50,
            Player(name="Player 2"): 50,
        }
    )

    company = Company(name="Company", shares=shares, buy_round=0, prices=[TotalPrice(100)])

    assert company.current_price() == TotalPrice(100)
    assert company.owners() == [Player(name="Player 1"), Player(name="Player 2")]

    assert (
        company.validate_player_share(Player(name="Player 1"), "100")
        == "Player 1 have only 50 shares"
    )

    assert company.validate_player_share(Player(name="Player 1"), "50") == True
    assert company.validate_player_share(Player(name="Player 2"), "50") == True

    company.trade_shares(
        log, Player(name="Player 1"), Player(name="Player 2"), 1, OneSharePrice(1)
    )

    assert pytest.approx(company.current_price()) == TotalPrice(100)

    assert company.validate_player_share(Player(name="Player 1"), "49") == True
    assert company.validate_player_share(Player(name="Player 2"), "51") == True

    try:
        company.trade_shares(
            log, Player(name="Player 2"), Player(name="Player 1"), 100, OneSharePrice(1)
        )
        assert False
    except ValueError as e:
        assert str(e) == "Player 2 does not have 100 shares"

    company.trade_shares(
        log, Player(name="Player 2"), Player(name="Player 1"), 10, OneSharePrice(2)
    )
    assert pytest.approx(company.current_price()) == TotalPrice(110)

    company.extend(1, Price(100))

    assert len(company.extension) == 1
    assert pytest.approx(company.current_price()) == TotalPrice(160)

    company.trade_shares(
        log, Player(name="Player 1"), Player(name="Player 2"), 10, OneSharePrice(1)
    )
    assert pytest.approx(company.current_price()) == TotalPrice(154)

    company.trade_shares(
        log, Player(name="Player 2"), Player(name="Player 1"), 10, OneSharePrice(1)
    )

    assert pytest.approx(company.current_price()) == TotalPrice(148.6)


def test_dividends() -> None:
    shares = Shares(
        players_share={
            Player(name="Player 1"): 20,
            Player(name="Player 2"): 30,
            Player(name="Player 3"): 50,
        }
    )

    company = Company(name="Company", shares=shares, buy_round=0, prices=[TotalPrice(100)])

    assert company.is_dividend_active() == False

    company.set_dividends(1, 2)

    assert company.is_dividend_active() == True

    assert company.next_dividend_round() == 3

    try:
        company.divident_paid(1, 100)
        assert False
    except ValueError as e:
        assert str(e) == "Dividends should not be paid"

    assert company.dividend_last_round == 1

    assert company.next_dividend_round() == 3
    assert company.is_dividend_active() == True

    company.divident_paid(3, 100)

    assert company.dividend_last_round == 3

    assert company.next_dividend_round() == 5
    assert company.is_dividend_active() == True
    assert company.current_price() == TotalPrice(0)
