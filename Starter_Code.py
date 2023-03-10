# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

import pandas
import numpy
import statistics
import math
import typing

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Listing, Product, Symbol, Position

# Dictionaries for converting between products and symbols
products: Dict[Product, Symbol]
symbols: Dict[Symbol, Product]

# Must be hard-coded, not accessible via TradingState. IMC will publish this
# information before each round, update here accordingly.
limits: Dict[Symbol, int] = {
    'PEARLS': 20,
    'BANANAS': 20,
}

def makeProductSymbolDicts(listings: Dict[Symbol, Listing]) -> None:
    """
    Converts the symbol -> listing dictionary into product -> symbol and symbol -> product dictionaries,
    stored as global variables.
    
    Parameters:
    listings (Dict[Symbol, Listing]): The dictionary of symbols to listings
    """
    global products
    global symbols
    products = {}
    symbols = {}
    
    for symbol in listings:
        product = listings[symbol]['product'] # Wiki is incorrect: Listing is a dict, not a class
        products[product] = symbol
        symbols[symbol] = product

def getBuySellVol(order_depth: OrderDepth, buy: bool) -> int:
    """
    Computes the total volume of either buy or sell orders from the given OrderDepth
    
    Parameters:
    order_depth (OrderDepth): The order depth to compute the volume from.
    buy (bool): Whether to compute the volume of buy orders or sell orders. True for buy, False for sell.
    
    Returns:
    int: The total volume of either buy or sell orders. Always positive.
    """
    
    total: int = 0

    if buy:
        for buy_order in order_depth.buy_orders:
            total += order_depth.buy_orders[buy_order]
    else:
        # Note the negation for sell orders, as they are negative in the order depth
        for sell_order in order_depth.sell_orders:
            total += -order_depth.sell_orders[sell_order]

    return total

def sortOrderDepth(order_depth: OrderDepth) -> None:
    """
    Sorts the buy_orders in the order depth in descending order and the sell_orders in ascending order
    
    Parameters:
    order_depth (OrderDepth): The order depth to sort
    
    Returns:
    None
    """
    buy_keys = list(order_depth.buy_orders.keys())
    buy_keys.sort(reverse=True)
    sorted_buy_orders = {i : order_depth.buy_orders[i] for i in buy_keys}

    sell_keys = list(order_depth.sell_orders.keys())
    sell_keys.sort()
    sorted_sell_orders = {i : order_depth.sell_orders[i] for i in sell_keys}

    order_depth.buy_orders = sorted_buy_orders
    order_depth.sell_orders = sorted_sell_orders

def getMarketActionValue(order_depth: OrderDepth, quantity: int, buy: bool) -> int:
    """
    Calculates the total value of a buy or sell order if it were to be executed at the market price
    
    Parameters:
    order_depth (OrderDepth): The order depth to use
    quantity (int): The quantity of the order
    buy (bool): Whether the order is a buy or sell order
    
    Returns:
    int: The total value of the market action
    """

    sortOrderDepth(order_depth)

    if buy:
        sell_orders = order_depth.sell_orders
        total_value = 0
        volume = 0
        for price in sell_orders:
            volume += -1 * sell_orders[price]
            if volume >= quantity:
                remaining_volume = quantity - (volume - (-1 * sell_orders[price]))
                total_value += price * remaining_volume
                break
            else:
                total_value += price * (-1 * sell_orders[price])
    else:
        buy_orders = order_depth.buy_orders
        total_value = 0
        volume = 0
        for price in buy_orders:
            volume += buy_orders[price]
            if volume >= quantity:
                remaining_volume = quantity - (volume - buy_orders[price])
                total_value += price * remaining_volume
                break
            else:
                total_value += price * buy_orders[price]
    
    return total_value

def getMarketActionVWAP(order_depth: OrderDepth, quantity: int, buy: bool) -> float:
    """
    Calculates the volume weighted average price of a buy or sell order if it were to be executed at the market price
    
    Parameters:
    order_depth (OrderDepth): The order depth to use
    quantity (int): The quantity to get the market action value for
    buy (bool): Whether the market action is a buy or a sell
    
    Returns:
    float: The volume weighted average price of the market action
    """

    total_value = getMarketActionValue(order_depth, quantity, buy)

    return total_value / quantity

def printOrderDepth(order_depth: OrderDepth) -> None:
    """
    Prints the order depth for a symbol
    
    Parameters:
    order_depth (OrderDepth): The order depth to print
        
    Returns:
    None
    """
    sortOrderDepth(order_depth)

    print("Buy Orders:")
    for price in order_depth.buy_orders:
        print("Price: " + str(price) + " Volume: " + str(order_depth.buy_orders[price]))
    
    print("Sell Orders:")
    for price in order_depth.sell_orders:
        print("Price: " + str(price) + " Volume: " + str(order_depth.sell_orders[price]))
        
def maxNewPosition(position: Dict[Product, Position], new_orders: Dict[Product, List[Order]],
    symbol: Symbol, buy: bool) -> int:
    """
    Computes the maximum quantity of a new position that can be opened for a given symbol in the
    given direction, considering position limits, the current position, and the orders to be
    executed by this strategy at the end of the time step.
    
    Parameters:
    position (Dict[Product, Position]): The current positions.
    new_orders (Dict[Product, List[Order]]): The orders that will be executed at the end of the current time step.
    symbol (Symbol): The symbol to compute the maximum position for.
    buy (bool): Whether the position is a buy or sell position. True for buy, False for sell.
    
    Returns:
    (int): The maximum quantity of a new position that can be opened for the given symbol, in the given direction.
    This number will be positive if buy is True, and negative if buy is False, unless the current position is already
    over the limit, in which case it will be negative if buy is True and positive if buy is False.
    """
    global limits
    global symbols
    
    # Instead of crashing when a symbol is not in limits or symbols, return a very large/small number
    if symbol not in limits or symbol not in symbols:
        return pow(10, 5) if buy else -pow(10, 5)
    
    product = symbols[symbol]
    
    # If there is no current position, assume it is 0
    current_position = 0
    if product in position:
        current_position = position[product]
    
    # If there are no new orders, assume the new position will be 0
    new_position = 0
    if product in new_orders:
        new_position = sum([order.quantity for order in new_orders[product]])
    
    # If the current position is already over the limit, return 0
    if buy:
        return max(limits[symbol] - current_position - new_position, 0)
    else:
        return min(-limits[symbol] - current_position - new_position, 0)

def addLimitOrder(new_orders: Dict[Product, List[Order]], position: Dict[Product, Position],
    symbol: Symbol, buy: bool, quantity: int, price: int) -> None:
    """
    Places a limit order at the given price and quantity. Checks the current positions and orders to ensure that the
    quantity does not exceed the maximum position limit.
    
    Parameters:
    new_orders (Dict[Product, List[Order]]): The orders that will be executed at the end of the current time step. This
    function will add a new order to this dictionary.
    position (Dict[Product, Position]): The current positions.
    symbol (Symbol): The symbol to place the order for.
    buy (bool): Whether the order is a buy or sell order. True for buy, False for sell.
    quantity (int): The quantity of the order.
    price (int): The price of the order.    
    """
    global symbols
    product = symbols[symbol]
    
    max_new = maxNewPosition(position, new_orders, symbol, buy)
    
    if buy:
        quantity = min(abs(quantity), abs(max_new))
    else:
        quantity = -min(abs(quantity), abs(max_new))
    
    if quantity != 0:
        if product not in new_orders:
            new_orders[product] = []
        
        new_orders[product].append(Order(symbol, price, quantity))

def addMarketOrders(new_orders: Dict[Product, List[Order]], position: Dict[Product, Position], symbol: Symbol, buy: bool,
    quantity: int, order_depths_after_mkt_orders: Dict[Symbol, OrderDepth]) -> None:
    """
    Places a market order for the given quantity. Checks the current positions and orders to ensure that the
    quantity does not exceed the maximum position limit. Fills orders at the market price until either the quantity we 
    want to fill is filled, or there are no more orders to fill. removes the filled orders from our created order depth.

    Parameters:
    new_orders (Dict[Product, List[Order]]): The orders that will be executed at the end of the current time step. This
    function will add new orders to this dictionary.
    position (Dict[Product, Position]): The current positions.
    symbol (Symbol): The symbol to place the order for.
    buy (bool): Whether the order is a buy or sell order. True for buy, False for sell.
    quantity (int): The quantity of the order.
    order_depths_after_mkt_orders (Dict[Symbol, OrderDepth]): Our order depths dict that we will remove from as we fill 
    market orders, preserving the state of the actual order_depths for this time step.

    Returns:
    None
    """
    global symbols
    product = symbols[symbol]

    max_new = maxNewPosition(position, new_orders, symbol, buy)

    if buy and quantity > max_new:
        quantity = max_new
    elif not buy and quantity > -max_new:
        quantity = max_new

    # make sure the order depth is sorted
    sortOrderDepth(order_depths_after_mkt_orders[symbol])

    # we will go through the lowest sell orders for a buy, and the highest buy orders for a sell
    orders = None
    if buy:
        orders = order_depths_after_mkt_orders[symbol].sell_orders
    else:
        orders = order_depths_after_mkt_orders[symbol].buy_orders

    volume_filled = 0
    remaining_quantity = 0
    if quantity != 0:
        if product not in new_orders:
            new_orders[product] = []
        
        for price in orders:

            volume_filled += orders[price]

            # Note: if there aren't enough orders to fill the quantity, we will fill as many as we can
            if volume_filled >= quantity:
                remaining_quantity = quantity - (volume_filled - orders[price])

                new_orders[product].append(Order(symbol, price, remaining_quantity))

                if remaining_quantity == orders[price]: # if the final order to be placed is the same size as the 
                    # matching order in the order book, we can just delete the order from the order book, otherwise, 
                    # we remove (from that order) the remaining quantity we need to fill
                    if buy:
                        del order_depths_after_mkt_orders[symbol].sell_orders[price]
                    else:
                        del order_depths_after_mkt_orders[symbol].buy_orders[price]
                else:
                    if buy:
                        order_depths_after_mkt_orders[symbol].sell_orders[price] -= remaining_quantity
                    else:
                        order_depths_after_mkt_orders[symbol].buy_orders[price] -= remaining_quantity
                break
            else: # delete orders from our order book as we fill them

                new_orders[product].append(Order(symbol, price, orders[price]))

                if buy:
                    del order_depths_after_mkt_orders[symbol].sell_orders[price]
                else:
                    del order_depths_after_mkt_orders[symbol].buy_orders[price]

class Trader:

    def run(self, state: TradingState) -> Dict[Product, List[Order]]:
        """
        Takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        
        # Create product/symbol dictionaries for later reference
        makeProductSymbolDicts(state.listings)
        global products
        global symbols
        order_depths_after_mkt_orders = state.order_depths 
        # ^ pass this to addMarketOrders, so that we can delete from it as we make multiple market orders in one time 
        # step while preserving the order depths in case we need to look at things such as highest bid and lowest ask
        
        result = {}
        return result