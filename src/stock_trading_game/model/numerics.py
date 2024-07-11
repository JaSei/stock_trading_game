from typing import NewType
import math

Price = NewType('Price', float)
TotalPrice = NewType('TotalPrice', float)
OneSharePrice = NewType('OneSharePrice', float)

PercentChange = NewType('PercentChange', float)

def ceil_price(price: Price | TotalPrice | OneSharePrice) -> str:
    ceil_price = math.ceil(price)
    ceil_price_str = "{:,}".format(ceil_price)
    return f"${ceil_price_str}"

def rounded_price(price: Price | TotalPrice | OneSharePrice) -> str:
    rounded_price = round(price, 2)
    rounded_price_str = "{:,}".format(rounded_price)
    return f"${rounded_price_str}"


def format_price(price: Price | TotalPrice | OneSharePrice) -> str:
    return f"{ceil_price(price)} [{rounded_price(price)}]"
