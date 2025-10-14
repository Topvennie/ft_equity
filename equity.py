from dataclasses import dataclass


@dataclass
class Equity:
    name: str
    ticker: str
    country: str
    sector: str
    industry: str
    market_cap: float | None
    dividend: float | None
    consensus: str
    price_to_earning: float | None
    price_to_book: float | None
    week_price_change: float | None
