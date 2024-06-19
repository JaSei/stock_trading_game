from stock_trading_game.company_kind import CompanyKind
from stock_trading_game.start_menu import parse_trading_csv


def test_parse_trading_csv() -> None:
    path = "tests/trading_data.csv"
    trading = parse_trading_csv(path)

    drevo = CompanyKind(name="Drevo", amount=5, initial_price=10)
    zlato = CompanyKind(name="Zlato", amount=3, initial_price=1000)

    assert trading.kinds == [drevo, zlato]
    assert drevo.amount == 5
    assert zlato.amount == 3
    assert drevo.initial_price == 10
    assert zlato.initial_price == 1000

    assert trading.trend(drevo) == [0.0, 0.01]
    assert trading.trend(zlato) == [0.02, 0.03]
