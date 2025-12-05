"""GBCE main exchange."""
from typing import Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP 
import math
from .stocks.common import CommonStock
from .stocks.preferred import PreferredStock
from .stocks.base import Stock

class GlobalBeverageCorpExchange:
    def __init__(self):
        self._stocks: Dict[str, Stock] = {}
    
    def create_common_stock(self, symbol: str, last_dividend: int, par_value: int) -> CommonStock:
        if symbol in self._stocks:
            raise ValueError(f"Stock {symbol} exists")
        stock = CommonStock(symbol, last_dividend, par_value)
        self._stocks[symbol] = stock
        return stock
    
    def create_preferred_stock(self, symbol: str, last_dividend: int, 
                             fixed_dividend_pct: float, par_value: int) -> PreferredStock:
        if symbol in self._stocks:
            raise ValueError(f"Stock {symbol} exists")
        stock = PreferredStock(symbol, last_dividend, fixed_dividend_pct, par_value)
        self._stocks[symbol] = stock
        return stock
    
    def get_stock(self, symbol: str) -> Stock:
        if symbol not in self._stocks:
            raise KeyError(f"Stock {symbol} not found")
        return self._stocks[symbol]
    
    def gbce_all_share_index(self) -> Optional[Decimal]:
        vwsps = [float(stock.volume_weighted_stock_price() or 0) 
                for stock in self._stocks.values()]
        vwsps = [v for v in vwsps if v > 0]
        if not vwsps:
            return None
        log_sum = sum(math.log(v) for v in vwsps)
        return Decimal(str(math.exp(log_sum / len(vwsps)))).quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    @property
    def stock_symbols(self) -> List[str]:
        return list(self._stocks.keys())
