from pydantic import BaseModel

from .numerics import Price, PercentChange


class CompanyKind(BaseModel):
    name: str
    amount: int
    initial_price: Price

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CompanyKind):
            return False
        return self.name == other.name

    def __str__(self) -> str:
        return f"{self.name} {self.amount} {self.initial_price}"

    def __repr__(self) -> str:
        return f"CompanyKind(name={self.name}, amount={self.amount}, initial_price={self.initial_price})"


class CompanyKindTrend(BaseModel):
    trend: list[PercentChange]

    def __str__(self) -> str:
        return f"{self.trend}"

    def __repr__(self) -> str:
        return f"CompanyKindTrend(trend={self.trend})"

    def add_trend(self, trend: PercentChange) -> None:
        self.trend.append(trend)
