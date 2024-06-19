from pydantic import BaseModel

class CompanyKind(BaseModel):
    name: str
    amount: int
    initial_price: float
    
    def __str__(self) -> str:
        return f"{self.name} {self.amount} {self.initial_price}"
    
    def __repr__(self) -> str:
        return f"CompanyKind(name={self.name}, amount={self.amount}, initial_price={self.initial_price})"

class CompanyKindTrend(BaseModel):
    trend: list[float]
    
    def __str__(self) -> str:
        return f"{self.trend}"
    
    def __repr__(self) -> str:
        return f"CompanyKindTrend(trend={self.trend})"

    def add_trend(self, trend: float) -> None:
        self.trend.append(trend)
