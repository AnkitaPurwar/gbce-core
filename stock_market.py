"""
Global Beverage Corporation Exchange (GBCE) - This Model Implements Phase 1 requirements for stock calculations and trading system.
All monetary values stored in pennies (integers) for precision.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
import math
from decimal import Decimal, ROUND_HALF_UP
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockType(Enum):
    """Stock classification for dividend calculation logic."""
    COMMON = "COMMON"
    PREFERRED = "PREFERRED"

class TradeIndicator(Enum):
    """Standardized trade direction indicator."""
    BUY = "BUY"
    SELL = "SELL"

@dataclass(frozen=True)
class Trade:
    """Immutable trade record."""
    timestamp: datetime
    quantity: int
    indicator: TradeIndicator
    price_pennies: int  # Price in pennies

class DividendCalculationError(Exception):
    """Raised when dividend calculation parameters are invalid."""
    pass

class Stock(ABC):
    """Abstract base for all stock types with core trading functionality."""
    
    def __init__(self, symbol: str, par_value_pennies: int):
        if not symbol or len(symbol) > 10:
            raise ValueError("Symbol must be 1-10 characters")
        if par_value_pennies <= 0:
            raise ValueError("Par value must be positive")
            
        self._symbol = symbol
        self._par_value_pennies = par_value_pennies
        self._trades: List[Trade] = []
        self._trade_lock = False  # Simple concurrency simulation
    
    @property
    def symbol(self) -> str:
        return self._symbol
    
    @property
    @abstractmethod
    def last_dividend_pennies(self) -> int:
        """Last dividend yield in pennies."""
        pass
    
    @abstractmethod
    def dividend_yield(self, price_pennies: int) -> Decimal:
        """Calculate dividend yield for given price."""
        pass
    
    def pe_ratio(self, price_pennies: int) -> Optional[Decimal]:
        """Price to Earnings ratio using last dividend as earnings proxy."""
        if price_pennies <= 0 or self.last_dividend_pennies == 0:
            return None
        return Decimal(price_pennies) / Decimal(self.last_dividend_pennies)
    
    def record_trade(self, quantity: int, indicator: TradeIndicator, 
                    price_pennies: int) -> None:
        """Record executed trade with validation."""
        self._validate_trade_params(quantity, indicator, price_pennies)
        
        trade = Trade(
            timestamp=datetime.now(),
            quantity=quantity,
            indicator=indicator,
            price_pennies=price_pennies
        )
        self._trades.append(trade)
        logger.info(f"Recorded {indicator.value} trade: {quantity} shares "
                   f"of {self.symbol} @ ${price_pennies/100:.2f}")
    
    def volume_weighted_stock_price(self, minutes_back: int = 5) -> Optional[Decimal]:
        """Volume Weighted Stock Price for recent trades."""
        cutoff = datetime.now() - timedelta(minutes=minutes_back)
        recent_trades = [t for t in self._trades if t.timestamp >= cutoff]
        
        if not recent_trades:
            return None
            
        total_quantity = sum(t.quantity for t in recent_trades)
        if total_quantity == 0:
            return None
        
        weighted_sum = sum(t.quantity * t.price_pennies for t in recent_trades)
        vwap_pennies = Decimal(weighted_sum) / Decimal(total_quantity)
        return (vwap_pennies / Decimal('100')).quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    def _validate_trade_params(self, quantity: int, indicator: TradeIndicator, 
                              price_pennies: int) -> None:
        """Validate trade parameters."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price_pennies <= 0:
            raise ValueError("Price must be positive")
    
    @property
    def trade_count(self) -> int:
        """Total number of recorded trades."""
        return len(self._trades)

class CommonStock(Stock):
    """Common stock implementation."""
    
    def __init__(self, symbol: str, last_dividend_pennies: int, par_value_pennies: int):
        super().__init__(symbol, par_value_pennies)
        if last_dividend_pennies < 0:
            raise ValueError("Last dividend cannot be negative")
        self._last_dividend_pennies = last_dividend_pennies
    
    @property
    def last_dividend_pennies(self) -> int:
        return self._last_dividend_pennies
    
    def dividend_yield(self, price_pennies: int) -> Decimal:
        if price_pennies <= 0:
            return Decimal('0')
        dividend = Decimal(self.last_dividend_pennies)
        return (dividend * Decimal('100') / Decimal(price_pennies)).quantize(Decimal('0.01'), ROUND_HALF_UP)

class PreferredStock(Stock):
    """Preferred stock with fixed dividend rate."""
    
    def __init__(self, symbol: str, last_dividend_pennies: int, 
                 fixed_dividend_percentage: float, par_value_pennies: int):
        super().__init__(symbol, par_value_pennies)
        if fixed_dividend_percentage <= 0 or fixed_dividend_percentage > 1.0:
            raise ValueError("Fixed dividend must be between 0 and 100%")
        self._last_dividend_pennies = last_dividend_pennies
        self._fixed_dividend_percentage = fixed_dividend_percentage
    
    @property
    def last_dividend_pennies(self) -> int:
        return self._last_dividend_pennies
    
    @property
    def fixed_dividend_percentage(self) -> float:
        return self._fixed_dividend_percentage
    
    def dividend_yield(self, price_pennies: int) -> Decimal:
        if price_pennies <= 0:
            return Decimal('0')
        fixed_dividend = Decimal(self._fixed_dividend_percentage) * Decimal(self._par_value_pennies)
        return (fixed_dividend * Decimal('100') / Decimal(price_pennies)).quantize(Decimal('0.01'), ROUND_HALF_UP)

class GlobalBeverageCorpExchange:
    """GBCE main exchange orchestrator."""
    
    def __init__(self):
        self._stocks: Dict[str, Stock] = {}
        self._stock_lock = False
    
    def create_common_stock(self, symbol: str, last_dividend_pennies: int, 
                           par_value_pennies: int) -> CommonStock:
        """Factory method for common stocks."""
        if symbol in self._stocks:
            raise ValueError(f"Stock {symbol} already exists")
        
        stock = CommonStock(symbol, last_dividend_pennies, par_value_pennies)
        self._stocks[symbol] = stock
        return stock
    
    def create_preferred_stock(self, symbol: str, last_dividend_pennies: int,
                              fixed_dividend_percentage: float, par_value_pennies: int) -> PreferredStock:
        """Factory method for preferred stocks."""
        if symbol in self._stocks:
            raise ValueError(f"Stock {symbol} already exists")
        
        stock = PreferredStock(symbol, last_dividend_pennies, fixed_dividend_percentage, par_value_pennies)
        self._stocks[symbol] = stock
        return stock
    
    def get_stock(self, symbol: str) -> Stock:
        """Retrieve stock by symbol."""
        if symbol not in self._stocks:
            raise KeyError(f"Stock {symbol} not found")
        return self._stocks[symbol]
    
    def gbce_all_share_index(self) -> Optional[Decimal]:
        """GBCE All-Share Index using geometric mean of VWSPs."""
        vwsps = []
        for stock in self._stocks.values():
            vwsp = stock.volume_weighted_stock_price()
            if vwsp is not None:
                vwsps.append(float(vwsp))
        
        if not vwsps:
            return None
        
        # Geometric mean using log-sum-exp for numerical stability
        log_sum = sum(math.log(v) for v in vwsps)
        geo_mean = math.exp(log_sum / len(vwsps))
        return Decimal(str(geo_mean)).quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    @property
    def stock_symbols(self) -> List[str]:
        """List of all stock symbols."""
        return list(self._stocks.keys())

# initialization with exact specifications (pennies)
def initialize_sample_exchange() -> GlobalBeverageCorpExchange:
    """Initialize GBCE with sample stock data."""
    exchange = GlobalBeverageCorpExchange()
    
    # Exact specifications: all values in pennies
    exchange.create_common_stock("TEA", 0, 10000)          
    exchange.create_common_stock("POP", 8, 10000)         
    exchange.create_common_stock("ALE", 23, 6000)           
    exchange.create_preferred_stock("GIN", 8, 0.02, 10000)  
    exchange.create_common_stock("JOE", 13, 25000)         
    
    logger.info("GBCE sample exchange initialized with 5 stocks")
    return exchange

# test suite
def run_demo():
    """Demonstrate system capabilities."""
    exchange = initialize_sample_exchange()
    
    tea = exchange.get_stock("TEA")
    gin = exchange.get_stock("GIN")
    
    # Dividend yield calculations ($100 = 10000 pennies)
    print(f"TEA dividend yield @$100: {tea.dividend_yield(10000)}%")
    print(f"GIN dividend yield @$100: {gin.dividend_yield(10000)}%")
    
    # Record trades
    tea.record_trade(1000, TradeIndicator.BUY, 9550)   # $95.50
    tea.record_trade(2000, TradeIndicator.SELL, 10230) # $102.30
    
    # metrics
    print(f"TEA VWSP (5min): ${tea.volume_weighted_stock_price()}")
    print(f"GBCE All-Share Index: ${exchange.gbce_all_share_index()}")

if __name__ == "__main__":
    run_demo()
