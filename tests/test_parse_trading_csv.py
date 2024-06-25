from stock_trading_game.model.company_kind import CompanyKind
from stock_trading_game.model.numerics import Price
from stock_trading_game.model.trading import Trading


def test_parse_trading_csv(trading: Trading) -> None:
    drevo = CompanyKind(name="Drevo", amount=5, initial_price=Price(10))
    zlato = CompanyKind(name="Zlato", amount=3, initial_price=Price(1000))

    assert trading.kinds == [drevo, zlato]
    assert drevo.amount == 5
    assert zlato.amount == 3
    assert drevo.initial_price == Price(10)
    assert zlato.initial_price == Price(1000)

    assert trading.trend(drevo) == [0.0, 0.01]
    assert trading.trend(zlato) == [0.02, 0.03]

    assert trading.max_rounds() == 2
