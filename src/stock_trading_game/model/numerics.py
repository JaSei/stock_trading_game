from typing import NewType

Price = NewType('Price', float)
PercentChange = NewType('PercentChange', float)

def format_price(price: Price) -> str:
    rounded_price = round(price, 2)
    desired_representation = "{:,}".format(rounded_price)
    return f"${desired_representation}" 
