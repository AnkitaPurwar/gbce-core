"""Immutable trade model."""
from dataclasses import dataclass
from datetime import datetime
from .enums import TradeIndicator

@dataclass(frozen=True)
class Trade:
    timestamp: datetime
    quantity: int
    indicator: TradeIndicator
    price_pennies: int
