from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from ..game import Game
from ..model.company import Company
from ..model.numerics import format_price


def print_shareholders(game: Game, company_filter: Optional[Company] = None) -> None:
    console = Console()

    tree = Tree("Shareholders")
    for company_kind in game.companies:
        company_kind_node = tree.add(company_kind.name)
        for company in game.companies[company_kind]:
            if isinstance(company, Company) and (company_filter is None or company_filter is company):
                company_node = company_kind_node.add(
                    f"{company.name} ({format_price(company.current_price())})"
                )
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Player")
                table.add_column("Share")
                table.add_column("Price")

                for player in company.owners():
                    table.add_row(
                        player.name,
                        str(company.owner_amount_of_shares(player)),
                        format_price(company.owner_shares_value(player)),
                    )

                company_node.add(table)

    console.print(tree)


