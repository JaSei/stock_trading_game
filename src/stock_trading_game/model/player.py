from pydantic import BaseModel

from .loan import Loan

class Player(BaseModel):
    name: str
    loans: list[Loan] = []

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.name == other.name


    def take_loan(self, loan: Loan) -> None:
        self.loans.append(loan)
