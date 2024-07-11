from pydantic import BaseModel, field_validator, model_serializer

from .player import Player

AMOUNT_OF_SHARES = 100


class Shares(BaseModel):
    players_share: dict[Player, int]

    @field_validator("players_share")
    @classmethod
    def players_share_sum_validator(cls, players_share: dict[Player, int]) -> dict[Player, int]:
        if sum(players_share.values()) != AMOUNT_OF_SHARES:
            raise ValueError(f"Sum of shares must be {AMOUNT_OF_SHARES}")
        return players_share

    @model_serializer
    def serialize(self) -> dict[str, int]:
        return {player.name: share for player, share in self.players_share.items()}

    def owners(self) -> list[Player]:
        return list(self.players_share.keys())

    def trade_shares(self, from_player: Player, to_player: Player, amount: int) -> None:
        if self.players_share[from_player] < amount:
            raise ValueError(f"{from_player.name} does not have {amount} shares")

        self.players_share[from_player] -= amount

        if to_player not in self.players_share:
            self.players_share[to_player] = 0

        self.players_share[to_player] += amount

    def validate_player_share(self, player: Player, amount: str) -> bool | str:
        if not amount.isdigit():
            return "Isn't a number"

        available_shares = self.players_share.get(player, 0)
        if int(amount) > available_shares:
            return f"{player.name} have only {available_shares} shares"
        return True

    def owner_amount_of_shares(self, owner: Player) -> int:
        try:
            return self.players_share[owner]
        except KeyError:
            return 0

    def owner_percent_share(self, owner: Player) -> float:
        return self.players_share[owner] / AMOUNT_OF_SHARES
