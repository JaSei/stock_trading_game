from stock_trading_game.model.company import Company
from stock_trading_game.model.player import Player
from stock_trading_game.model.shares import Shares
from stock_trading_game.model.numerics import Price


def test_company() -> None:
    shares = Shares(
        players_share={
            Player(name="Player 1"): 50,
            Player(name="Player 2"): 50,
        }
    )

    company = Company(name="Company", shares=shares, buy_round=0, prices=[Price(100)])

    assert company.current_price() == Price(100)
    assert company.owners() == [Player(name="Player 1"), Player(name="Player 2")]

    assert company.validate_player_share(Player(name="Player 1"), '100') == "Player 1 have only 50 shares"

    assert company.validate_player_share(Player(name="Player 1"), '50') == True
    assert company.validate_player_share(Player(name="Player 2"), '50') == True

    company.trade_shares(Player(name="Player 1"), Player(name="Player 2"), 1)

    assert company.validate_player_share(Player(name="Player 1"), '49') == True
    assert company.validate_player_share(Player(name="Player 2"), '51') == True

    try:
        company.trade_shares(Player(name="Player 2"), Player(name="Player 1"), 100)
        assert False
    except ValueError as e:
        assert str(e) == "Player 2 does not have 100 shares"
