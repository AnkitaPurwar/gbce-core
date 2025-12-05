# Global Beverage Corporation Exchange (GBCE) - Core Trading System

Production-ready **Phase 1** object-oriented core model for the Global Beverage Corporation Exchange (GBCE), a specialized stock market for drinks companies.

## 🚀 Features

- **Dividend Yield** calculations for Common & Preferred stocks
- **P/E Ratio** using last dividend as earnings proxy
- **Trade Recording** with timestamp, quantity, BUY/SELL indicator, price (pennies)
- **Volume Weighted Stock Price (VWSP)** for trades in past 5 minutes
- **GBCE All-Share Index** via geometric mean of all VWSPs
- **Penny Precision** - All monetary values as integers (eliminates float errors)
- **SOLID Architecture** with abstract base classes and factory methods

## 📊 Supported Stocks

| Symbol | Type      | Last Dividend | Fixed Dividend | Par Value |
|--------|-----------|---------------|----------------|-----------|
| TEA    | Common    | $0.00 (0¢)    | -              | $100.00   |
| POP    | Common    | $0.08 (8¢)    | -              | $100.00   |
| ALE    | Common    | $0.23 (23¢)   | -              | $60.00    |
| GIN    | Preferred | $0.08 (8¢)    | 2%             | $100.00   |
| JOE    | Common    | $0.13 (13¢)   | -              | $250.00   |




##  Key Design Decisions

- **Penny Precision**: All prices/dividends/par values as `int` pennies (`10000` = $100.00)
- **Decimal Arithmetic**: Output calculations use `Decimal` for financial precision
- **Immutable Trades**: `@dataclass(frozen=True)` prevents accidental mutation
- **Type Safety**: Full typing with `Enum`, `Optional[Decimal]`, abstract methods
- **Production Logging**: Structured logs for trade recording and initialization 



##  Formulas Implemented

**Dividend Yield**: `Common: (Last Dividend × 100) ÷ Price`
                    `Preferred: (Fixed Dividend × Par Value × 100) ÷ Price`

**P/E Ratio**: `Price ÷ Last Dividend`

**VWSP**: `Σ(Quantity × Price) ÷ Σ(Quantity)` (past 5 minutes)

**GBCE Index**: `exp(Σ(ln(VWSP)) ÷ n)` - Geometric mean


## 📁 Project Structure
gbce-core/ # ← Run pip install -e . HERE
`├── pyproject.toml # Hatchling build config (packages = ["gbce"])
├── README.md # This file
└── gbce/ # ← MAIN PACKAGE (python -m gbce)
├── __init__.py # Exports: GlobalBeverageCorpExchange
├── __main__.py # python -m gbce entrypoint
├── models/ # Data models
│ ├── init.py
│ ├── enums.py # TradeIndicator (BUY/SELL)
│ └── trade.py # Immutable Trade dataclass
├── stocks/ # Stock implementations
│ ├── init.py
│ ├── base.py # Stock(ABC)
│ ├── common.py # CommonStock
│ └── preferred.py # PreferredStock
└── exchange.py # GlobalBeverageCorpExchange`


💻 Usage Examples

## Basic Operations

from gbce import GlobalBeverageCorpExchange
from gbce.models.enums import TradeIndicator

exchange = GlobalBeverageCorpExchange()

# Create stocks (pennies)
tea = exchange.create_common_stock("TEA", 0, 10000)  # $100 par

# Calculations ($100 = 10000 pennies)
print(f"Dividend Yield: {tea.dividend_yield(10000)}%")  # 0.00%
print(f"P/E Ratio: {tea.pe_ratio(10000)}")              # None

# Record trade
tea.record_trade(1000, TradeIndicator.BUY, 9550)  # $95.50

print(f"VWSP: ${tea.volume_weighted_stock_price()}")     # $95.50
print(f"GBCE: ${exchange.gbce_all_share_index()}")       # None (no VWSPs)

# Requirements

Python >= 3.8 (stdlib only - no external deps)
decimal (built-in)
logging (built-in)

# Development Setup
`
# Clone and install
 - git clone https://github.com/AnkitaPurwar/gbce-core.git
 - cd gbce-core

# Install dev tools
 - pip install -e .
 - python -m gbce

or 
 - pip install -e . && python -m gbce 



## 🔧 Troubleshooting

| ❌ Error | ✅ Solution |
|----------|-------------|
| `pip install -e .` fails | `packages = ["gbce"]` in `pyproject.toml` |

