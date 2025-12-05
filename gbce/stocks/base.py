"""Abstract Stock base class."""
from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from ..models.trade import Trade
from ..models.enums import TradeIndicator
import logging

logger = logging.getLogger(__name__)

class Stock(ABC):
    def __init__(self, symbol: str, par_value_pennies: int):
        if not symbol or len(symbol) > 10:
            raise ValueError("Invalid symbol")
        if par_value_pennies <= 0:
            raise ValueError("Invalid par value")
        self._symbol = symbol
        self._par_value_pennies = par_value_pennies
        self._trades: List[Trade] = []
    
    @property
    def symbol(self) -> str:
        return self._symbol
    
    @abstractmethod
    def dividend_yield(self, price_pennies: int) -> Decimal:
        pass
    
    @property
    @abstractmethod
    def last_dividend_pennies(self) -> int:
        pass
    
    def pe_ratio(self, price_pennies: int) -> Optional[Decimal]:
        if price_pennies <= 0 or self.last_dividend_pennies == 0:
            return None
        return Decimal(price_pennies) / Decimal(self.last_dividend_pennies)
    
    def record_trade(self, quantity: int, indicator: TradeIndicator, price_pennies: int) -> None:
        if quantity <= 0 or price_pennies <= 0:
            raise ValueError("Invalid trade params")
        trade = Trade(datetime.now(), quantity, indicator, price_pennies)
        self._trades.append(trade)
        logger.info(f"Trade: {quantity} {self.symbol} @ ${price_pennies/100:.2f}")
    
    def volume_weighted_stock_price(self, minutes_back: int = 5) -> Optional[Decimal]:
        cutoff = datetime.now() - timedelta(minutes=minutes_back)
        recent = [t for t in self._trades if t.timestamp >= cutoff]
        if not recent:
            return None
        total_qty = sum(t.quantity for t in recent)
        if total_qty == 0:
            return None
        weighted = sum(t.quantity * t.price_pennies for t in recent)
        vwap = Decimal(weighted) / Decimal(total_qty) / Decimal(100)
        return vwap.quantize(Decimal('0.01'), ROUND_HALF_UP)
