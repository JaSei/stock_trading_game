from .player import Player
from .trading import Trading
from .company_kind import CompanyKind
from .numerics import PercentChange, Price


class Game:
    def __init__(self, players: list[Player], trading: Trading) -> None:
        self.players = players
        self.trading = trading
        self.round = 0
        self.rounds_price: dict[CompanyKind, list[Price]] = {
            kind: [kind.initial_price] for kind in trading.kinds
        }

    def shift_to_round(self, round: int) -> None:
        for _ in range(self.round, round):
            self.shift_to_next_round()

    # return the next round number
    def next_round(self) -> int:
        return self.round + 1

    def next_round_kind_trend(self, kind: CompanyKind) -> PercentChange:
        return self.trading.trend(kind)[self.round]

    def current_round_price(self, kind: CompanyKind) -> Price:
        return self.rounds_price[kind][self.round]

    def shift_to_next_round(
        self, next_round_extra_percent_change: dict[CompanyKind, PercentChange] = {}
    ) -> None:
        for kind in self.trading.kinds:
            price = Price(
                self.current_round_price(kind)
                * (
                    1
                    + self.next_round_kind_trend(kind)
                    + next_round_extra_percent_change.get(kind, 0)
                )
            )
            self.rounds_price[kind].append(price)

        self.round += 1
