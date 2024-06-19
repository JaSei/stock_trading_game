from pydantic import BaseModel

from .company_kind import CompanyKind, CompanyKindTrend

class Trading(BaseModel):
    kinds: list[CompanyKind]
    trends: list[CompanyKindTrend]

    def trend(self, kind: CompanyKind) -> list[float]:
        for i in range(len(self.kinds)):
            if self.kinds[i] == kind:
                return self.trends[i].trend
        return []
