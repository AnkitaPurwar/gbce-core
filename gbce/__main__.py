"""GBCE main executable."""
from .exchange import GlobalBeverageCorpExchange
from .models.enums import TradeIndicator

def main():
    exchange = GlobalBeverageCorpExchange()
    
    # Phase 1 stocks (pennies)
    exchange.create_common_stock("TEA", 0, 10000)
    exchange.create_common_stock("POP", 8, 10000)
    exchange.create_common_stock("ALE", 23, 6000)
    exchange.create_preferred_stock("GIN", 8, 0.02, 10000)
    exchange.create_common_stock("JOE", 13, 25000)
    
    tea = exchange.get_stock("TEA")
    print(f"TEA yield @$100: {tea.dividend_yield(10000)}%")
    
    tea.record_trade(1000, TradeIndicator.BUY, 9550)
    tea.record_trade(2000, TradeIndicator.SELL, 10230)
    
    print(f"TEA VWSP: ${tea.volume_weighted_stock_price()}")
    print(f"GBCE Index: ${exchange.gbce_all_share_index()}")

if __name__ == "__main__":
    main()
