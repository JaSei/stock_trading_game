from pydantic import BaseModel, ConfigDict

from .shares import Shares, AMOUNT_OF_SHARES
from .numerics import Price, format_price
from .player import Player


class Company(BaseModel):
    name: str
    shares: Shares
    buy_round: int
    prices: list[Price]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self) -> str:
        return f"{self.name} ({format_price(self.current_price())})"

    def current_price(self) -> Price:
        return self.prices[-1]

    def current_one_share_price(self) -> Price:
        return Price(self.current_price() / AMOUNT_OF_SHARES)

    def owners(self) -> list[Player]:
        return self.shares.owners()

    def owner_amount_of_shares(self, owner: Player) -> int:
        return self.shares.owner_amount_of_shares(owner)

    def owner_shares_value(self, owner: Player) -> Price:
        return Price(self.current_one_share_price() * self.owner_amount_of_shares(owner))

    def trade_shares(self, from_player: Player, to_player: Player, amount: int) -> None:
        self.shares.trade_shares(from_player, to_player, amount)

    def validate_player_share(self, player: Player, amount: str) -> bool | str:
        return self.shares.validate_player_share(player, amount)


class CompanyPlaceholder(BaseModel):

    def __str__(self) -> str:
        return "CompanyPlaceholder"
