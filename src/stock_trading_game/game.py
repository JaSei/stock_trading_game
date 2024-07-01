import json
from typing import Any, Optional

from .model.company import Company, CompanyPlaceholder
from .model.company_kind import CompanyKind
from .model.numerics import PercentChange, TotalPrice
from .model.player import Player
from .model.shares import Shares
from .model.trading import Trading


class Game:
    def __init__(self, players: list[Player], trading: Trading) -> None:
        self.players = players
        self.trading = trading
        self.round = 0
        self.rounds_price: dict[CompanyKind, list[TotalPrice]] = {
            kind: [kind.initial_price] for kind in trading.kinds
        }
        self.companies: dict[CompanyKind, list[Company | CompanyPlaceholder]] = {
            kind: [CompanyPlaceholder() for _ in range(kind.amount)] for kind in trading.kinds
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Game):
            return NotImplemented

        return (
            self.players == other.players
            and self.trading == other.trading
            and self.round == other.round
            and self.rounds_price == other.rounds_price
            and self.companies == other.companies
        )

    @staticmethod
    def load_from(path: str) -> "Game":
        with open(path) as f:
            data = json.load(f)

        kinds: dict[str, CompanyKind] = {
            kind["name"]: CompanyKind(**kind) for kind in data["trading"]["kinds"]
        }

        players = [Player(**player) for player in data["players"]]
        trading = Trading(kinds=data["trading"]["kinds"], trends=data["trading"]["trends"])
        game = Game(players=players, trading=trading)
        game.round = data["round"]
        game.rounds_price = {
            kinds[kind_name]: [TotalPrice(price) for price in prices]
            for kind_name, prices in data["rounds_price"].items()
        }
        game.companies = {
            kinds[kind_name]: [
                (
                    Company(
                        name=company["name"],
                        shares=Shares(
                            players_share={
                                Player(name=player_name): share
                                for player_name, share in company["shares"].items()
                            }
                        ),
                        buy_round=company["buy_round"],
                        prices=[TotalPrice(price) for price in company["prices"]],
                        extension=company.get("extension", 0),
                        dividend_period=company.get("dividend_period", None),
                        dividend_last_round=company.get("dividend_last_round", None),
                    )
                    if "shares" in company
                    else CompanyPlaceholder()
                )
                for company in companies
            ]
            for kind_name, companies in data["companies"].items()
        }

        return game

    def model_dump(self) -> dict[str, Any]:
        return {
            "players": [player.model_dump() for player in self.players],
            "trading": self.trading.model_dump(),
            "round": self.round,
            "rounds_price": {
                kind.name: [float(price) for price in prices]
                for kind, prices in self.rounds_price.items()
            },
            "companies": {
                kind.name: [company.model_dump() for company in companies]
                for kind, companies in self.companies.items()
            },
        }

    def shift_to_round(self, round: int) -> None:
        for _ in range(self.round, round):
            self.shift_to_next_round()

    # return the next round number
    def next_round(self) -> int:
        return self.round + 1

    def next_round_kind_trend(self, kind: CompanyKind) -> PercentChange:
        return self.trading.trend(kind)[self.round]

    def current_round_price(self, kind: CompanyKind) -> TotalPrice:
        return self.rounds_price[kind][self.round]

    def average_price(self, kind: CompanyKind) -> TotalPrice:
        try:
            return TotalPrice(
                sum([company.current_price() for company in self.tradable_companies_by_kind(kind)])
                / len(self.tradable_companies_by_kind(kind))
            )
        except ZeroDivisionError:
            return TotalPrice(0)

    def tradable_companies_by_kind(self, kind: CompanyKind) -> list[Company]:
        return [company for company in self.companies[kind] if isinstance(company, Company)]

    def shift_to_next_round(
        self, next_round_extra_percent_change: dict[CompanyKind, PercentChange] = {}
    ) -> None:
        for kind in self.trading.kinds:
            price = TotalPrice(
                self.current_round_price(kind)
                * (
                    1
                    + self.next_round_kind_trend(kind)
                    + next_round_extra_percent_change.get(kind, 0)
                )
            )
            self.rounds_price[kind].append(price)

        for kind in self.companies:
            for company in self.companies[kind]:
                if isinstance(company, Company):
                    price = TotalPrice(
                        company.current_price()
                        * (
                            1
                            + self.next_round_kind_trend(kind)
                            + next_round_extra_percent_change.get(kind, 0)
                        )
                    )

                    company.prices.append(price)

        self.round += 1

    # row is round, column (index) is kind
    def rounds_price_list(self) -> list[list[TotalPrice]]:
        kind_based_matrix = [self.rounds_price[kind] for kind in self.trading.kinds]
        return list(map(list, zip(*kind_based_matrix)))

    def max_companies(self) -> int:
        return max([kind.amount for kind in self.trading.kinds])

    def companies_list(self) -> list[list[Optional[Company | CompanyPlaceholder]]]:
        rows = []
        for i in range(self.max_companies()):
            row: list[Optional[Company | CompanyPlaceholder]] = []
            for kind in self.trading.kinds:
                if i >= len(self.companies[kind]):
                    row.append(None)
                else:
                    row.append(self.companies[kind][i])
            rows.append(row)

        return rows

    def tradable_companies(self) -> list[Company]:
        return [
            company
            for kind in self.trading.kinds
            for company in self.companies[kind]
            if isinstance(company, Company)
        ]

    def bank_companies(self) -> list[Company]:
        return [company for company in self.tradable_companies() if self.bank() in company.owners()]

    def company_kind_by_name(self, name: str) -> CompanyKind:
        return next(filter(lambda k: k.name == name, self.trading.kinds))

    def is_some_free_company_kind_left(self, kind_or_name: CompanyKind | str) -> bool:
        if isinstance(kind_or_name, str):
            kind = self.company_kind_by_name(kind_or_name)
        else:
            kind = kind_or_name

        return any(isinstance(company, CompanyPlaceholder) for company in self.companies[kind])

    def get_free_company_kinds(self) -> list[CompanyKind]:
        return [kind for kind in self.trading.kinds if self.is_some_free_company_kind_left(kind)]

    def buy_company(
        self, kind: CompanyKind, name: str, players_share: dict[Player, int], price: TotalPrice
    ) -> None:
        # replace first CompanyPlaceholder with a new Company or raise an error
        for i, company in enumerate(self.companies[kind]):
            if isinstance(company, CompanyPlaceholder):
                self.companies[kind][i] = Company(
                    name=name,
                    shares=Shares(players_share=players_share),
                    buy_round=self.round,
                    prices=[price],
                )
                break
        else:
            raise ValueError("No free company left")

    def company_by_name(self, name: str) -> Company:
        for kind in self.trading.kinds:
            for company in self.companies[kind]:
                if isinstance(company, Company) and company.name == name:
                    return company

        raise ValueError(f"Company {name} not found")

    def validate_company_name(self, name: str) -> bool | str:
        if name == "":
            return "Invalid name"

        try:
            self.company_by_name(name)
            return "Name already taken"
        except ValueError:
            return True

    def save_to(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.model_dump(), f)

    def bank(self) -> Player:
        return next(filter(lambda p: p.name == "Bank", self.players))

    def list_companies_with_dividends(self) -> list[Company]:
        return [company for company in self.tradable_companies() if company.is_dividend_active()]

    def list_companies_without_dividents(self) -> list[Company]:
        return [company for company in self.tradable_companies() if not company.is_dividend_active()]

    def get_player_by_name(self, name: str) -> Player:
        return next(filter(lambda p: p.name == name, self.players))
