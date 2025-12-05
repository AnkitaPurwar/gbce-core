"""Common stock implementation."""
from decimal import Decimal, ROUND_HALF_UP
from .base import Stock

class CommonStock(Stock):
    def __init__(self, symbol: str, last_dividend_pennies: int, par_value_pennies: int):
        super().__init__(symbol, par_value_pennies)
        if last_dividend_pennies < 0:
            raise ValueError("Invalid dividend")
        self._last_dividend_pennies = last_dividend_pennies
    
    @property
    def last_dividend_pennies(self) -> int:
        return self._last_dividend_pennies
    
    def dividend_yield(self, price_pennies: int) -> Decimal:
        if price_pennies <= 0:
            return Decimal('0.00')
        return (Decimal(self.last_dividend_pennies) * Decimal(100) / 
                Decimal(price_pennies)).quantize(Decimal('0.01'), ROUND_HALF_UP)
