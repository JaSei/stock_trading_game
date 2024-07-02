import csv

from pydantic import BaseModel

from .company_kind import CompanyKind, CompanyKindTrend
from .numerics import PercentChange
from .company_kind import CompanyKind, CompanyKindTrend
from .numerics import PercentChange, TotalPrice


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
            print(
                f"{kind.name} ({kind.amount} companies) - {len(self.trend(kind))} trend data points"
            )

    def max_rounds(self) -> int:
        return len(self.trends[0].trend)


# first column is only metadata, it can be skipped
# first row is CompanyKind
# second row means amount of companies in the CompanyKind
# third row is initial CompanyKind price in round 0
# fourth row and rest are CompanyKindTrend (percentage change in double format)
def parse_trading_csv(path: str) -> Trading:
    print(f"Parsing trading data from {path}...")

    company_kinds = []
    with open(path) as file:
        reader = csv.reader(file)
        company_kind = next(reader)[1:]
        company_kind_amount = list(map(int, next(reader)[1:]))
        company_kind_price = list(map(float, next(reader)[1:]))

        for i in range(len(company_kind)):
            kind = CompanyKind(
                name=company_kind[i],
                amount=company_kind_amount[i],
                initial_price=TotalPrice(company_kind_price[i]),
            )
            company_kinds.append(kind)

        trend_data: list[CompanyKindTrend] = []
        for i, kind in enumerate(company_kinds):
            trend_data.append(CompanyKindTrend(trend=[]))

        for row in reader:
            for i, value in enumerate(row[1:]):
                trend_data[i].add_trend(PercentChange(float(value.replace(",", "."))))

    return Trading(kinds=company_kinds, trends=trend_data)
