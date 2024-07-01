from pydantic import BaseModel

from .numerics import Price


class Loan(BaseModel):
    amount: int
    interest_rate: int
    duration: int
    start_round: int
    paid: bool = False

    def final_amount(self) -> Price:
        return Price(self.amount * (1 + self.interest_rate / 100))

    def is_active(self) -> bool:
        return not self.paid

    def is_pay_off_round(self, current_round: int) -> bool:
        return current_round == self.target_round()

    def pay_off(self) -> None:
        self.paid = True

    def target_round(self) -> int:
        return self.start_round + self.duration
