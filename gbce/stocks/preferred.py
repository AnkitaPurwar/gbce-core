"""Preferred stock implementation."""
from decimal import Decimal, ROUND_HALF_UP
from .base import Stock

class PreferredStock(Stock):
    def __init__(self, symbol: str, last_dividend_pennies: int, 
                 fixed_dividend_pct: float, par_value_pennies: int):
        super().__init__(symbol, par_value_pennies)
        if not 0 < fixed_dividend_pct <= 1.0:
            raise ValueError("Invalid fixed dividend")
        self._last_dividend_pennies = last_dividend_pennies
        self._fixed_dividend_pct = fixed_dividend_pct
    
    @property
    def last_dividend_pennies(self) -> int:
        return self._last_dividend_pennies
    
    @property
    def fixed_dividend_percentage(self) -> float:
        return self._fixed_dividend_pct
    
    def dividend_yield(self, price_pennies: int) -> Decimal:
        if price_pennies <= 0:
            return Decimal('0.00')
        fixed_div = Decimal(self._fixed_dividend_pct) * Decimal(self._par_value_pennies)
        return (fixed_div * Decimal(100) / Decimal(price_pennies)).quantize(Decimal('0.01'), ROUND_HALF_UP)
