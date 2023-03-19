# Basic strategy to print the order book and market trades

from typing import Dict, List
from datamodel import Product, Order, TradingState

class Trader:
    def run(self, state: TradingState) -> Dict[Product, List[Order]]:
        print("Order book:")
        for symbol in state.order_depths:
            for price in state.order_depths[symbol].buy_orders:
                print("BUY", "symbol:", symbol, "price:", price, "quantity:", state.order_depths[symbol].buy_orders[price])
            for price in state.order_depths[symbol].sell_orders:
                print("SELL", "symbol:", symbol, "price:", price, "quantity:", state.order_depths[symbol].sell_orders[price])
                
        print("Market orders:")
        for symbol in state.market_trades:
            for trade in state.market_trades[symbol]:
                print("symbol:", symbol, "price:", trade.price, "quantity:", trade.quantity, "buyer:", trade.buyer, "seller:", trade.seller)
        
        
        return {}
