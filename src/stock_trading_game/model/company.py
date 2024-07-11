from logging import Logger
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .numerics import OneSharePrice, Price, TotalPrice, format_price
from .player import Player
from .shares import AMOUNT_OF_SHARES, Shares

EXTENSION_PERCENTAGE = 0.5


class Company(BaseModel):
    name: str
    shares: Shares
    buy_round: int
    prices: list[TotalPrice]
    extension: list[int] = []
    dividend_period: Optional[int] = None
    dividend_last_round: Optional[int] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self) -> str:
        extensions = "🏢" * len(self.extension)
        return f"{self.name} ({format_price(self.current_price())}) {extensions}"

    def current_price(self) -> TotalPrice:
        return self.prices[-1]

    def current_one_share_price(self) -> OneSharePrice:
        return OneSharePrice(self.current_price() / AMOUNT_OF_SHARES)

    def owners(self) -> list[Player]:
        return self.shares.owners()

    def owner_amount_of_shares(self, owner: Player) -> int:
        return self.shares.owner_amount_of_shares(owner)

    def owner_percent_share(self, owner: Player) -> float:
        return self.shares.owner_percent_share(owner)

    def owner_shares_value(self, owner: Player) -> TotalPrice:
        return TotalPrice(self.current_one_share_price() * self.owner_amount_of_shares(owner))

    def trade_shares(
        self,
        log: Logger,
        from_player: Player,
        to_player: Player,
        amount: int,
        price_per_share: OneSharePrice,
    ) -> None:
        log.info(f"Company before trade: {self}")

        log.info(
            f"Trade: {from_player.name} -> {to_player.name} {amount} shares for {price_per_share} each"
        )

        self.shares.trade_shares(from_player, to_player, amount)

        # the trade price procentually affects the company price
        unaffected_price = self.current_price() - self.current_one_share_price() * amount
        self.prices[-1] = TotalPrice(unaffected_price + price_per_share * amount)

        log.info(f"Company after trade: {self}")

    def validate_player_share(self, player: Player, amount: str) -> bool | str:
        return self.shares.validate_player_share(player, amount)

    def extend(self, game_round: int, price: Price) -> None:
        self.extension.append(game_round)
        self.prices[-1] = TotalPrice(self.current_price() + price * EXTENSION_PERCENTAGE)

    def has_built_extension(self, game_round: int) -> bool:
        return game_round in self.extension

    def next_dividend_round(self) -> int:
        if self.dividend_last_round is None:
            raise ValueError("No dividends were paid yet")
        if self.dividend_period is None:
            raise ValueError("Dividends are not set")

        return self.dividend_last_round + self.dividend_period

    def is_dividend_active(self) -> bool:
        return self.dividend_period is not None

    def set_dividends(self, game_round: int, dividend_period: int) -> None:
        self.dividend_period = dividend_period
        self.dividend_last_round = game_round

    def disable_dividends(self) -> None:
        self.dividend_period = None
        self.dividend_last_round = None

    # check if dividends should be paid in this round
    # return a dictionary with players and their dividends
    # or None if dividends should not be paid
    def is_dividend_round(self, game_round: int) -> bool:
        return self.is_dividend_active() and game_round == self.next_dividend_round()

    def divident_paid(self, game_round: int, total_dividend: int) -> None:
        if not self.is_dividend_round(game_round):
            raise ValueError("Dividends should not be paid")

        self.dividend_last_round = game_round
        self.prices[-1] = TotalPrice(self.current_price() - total_dividend)


class CompanyPlaceholder(BaseModel):

    def __str__(self) -> str:
        return "CompanyPlaceholder"
