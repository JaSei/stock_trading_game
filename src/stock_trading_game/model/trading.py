from pydantic import BaseModel

from .company_kind import CompanyKind, CompanyKindTrend
from .numerics import PercentChange

class Trading(BaseModel):
    kinds: list[CompanyKind]
    trends: list[CompanyKindTrend]

    def trend(self, kind: CompanyKind) -> list[PercentChange]:
        for i in range(len(self.kinds)):
            if self.kinds[i] == kind:
                return self.trends[i].trend
        return []

    def print_summary(self) -> None:
        for kind in self.kinds:
            print(f"{kind.name} ({kind.amount} companies) - {len(self.trend(kind))} trend data points")
    
    def max_rounds(self) -> int:
        return len(self.trends[0].trend)
