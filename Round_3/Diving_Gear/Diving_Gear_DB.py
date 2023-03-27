# Combined Strategy for Bananas and Pearls

import math
import numpy as np

from typing import Dict, List, Callable, Any, TypeVar
from datamodel import OrderDepth, TradingState, Order, Listing, Product, Symbol, Position

# Dictionaries for converting between products and symbols
products: Dict[Product, Symbol] = {}
symbols: Dict[Symbol, Product] = {}

# Must be hard-coded, not accessible via TradingState. IMC will publish this
# information before each round, update here accordingly.
limits: Dict[Symbol, int] = {
    'PEARLS': 20,
    'BANANAS': 20,
    'DIVING_GEAR': 50
}

diving_gear_distribution: Dict[int, float] = {
    -1: 1,
    1: 1
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

T = TypeVar('T')
def distributeValue(value: int, probabilities: Dict[T, float]) -> Dict[T, int]:
    """
    Distributes the given value among the given probabilities. The probabilities are given as a dictionary
    of any type to a float, which represents the distribution probability of that type. The returned dictionary
    will map the supplied types to integers, which represent the amount of the value that should be distributed
    into that bucket. The distribution will be rounded down, and the remaining value will be distributed
    into the **lowest probability buckets**.
    
    Parameters:
    value (int): The total value to distribute.
    probabilities (Dict[T, float]): The probabilities of each bucket.
    
    Returns:
    Dict[T, int]: The distribution of the value among the buckets.
    """
    # Distribute the value into the buckets, rounding down
    values: Dict[T, int] = {p: math.floor(value * probabilities[p]) for p in probabilities}
    remaining = value - sum(value for value in values.values())
    
    # Sort the probabilities in descending order
    descending_keys = sorted(probabilities, key=lambda p: probabilities[p], reverse=True)
    
    # Distribute the remaining value into the lowest probability buckets
    for key in descending_keys:
        if remaining <= 0:
            break
        
        values[key] += 1 # Add one to the bucket
        remaining -= 1 # Subtract one from the remaining value
        
    return values

class Strategy:
    """
    A simple trading strategy class that makes it easier to write strategies and especially to track
    any associated data that should persist data across time steps.
    """
    
    def __init__(self, symbol: Symbol, pos_limit: Position, strategy: Callable[[Any, TradingState], None]):
        """
        Create a new strategy. The run function should take this Strategy instance, and a TradingState.
        """
        self.symbol = symbol
        self.pos_limit = pos_limit
        global symbols
        self.product = symbols[symbol] if symbol in symbols else symbol
        self.strategy = strategy
        self.data: Dict[Any, Any] = {} # A dictionary of data that persists across time steps

    def run(self, state: TradingState) -> List[Order]:
        """
        Run this strategy for the given TradingState. This function will return a list of orders to be executed
        for this strategy's symbol at the end of the time step.
        """
        self.my_orders: List[Order] = []
        self.order_depth_after_mkt_orders = state.order_depths[self.symbol] if \
            self.symbol in state.order_depths else OrderDepth()
        self.strategy(self, state)
        return self.my_orders

    def maxNewPosition(self, current_position: Position, buy: bool) -> int:
        """
        Computes the maximum quantity of a new position that can be opened for this strategy's symbol in the
        given direction, considering position limits, the current position, and the orders to be executed by
        this strategy at the end of the time step.
        
        Parameters:
        current_position (Position): The current position for this strategy's symbol.
        buy (bool): Whether the position is a buy or sell position. True for buy, False for sell.
        
        Returns:
        (int): The maximum quantity of a new position that can be opened in the given direction. This number will be
        positive if buy is True, and negative if buy is False, unless the current position is already over the limit,
        in which case it will be 0.
        """
        
        # Positions are restricted to the following conditions:
        # 1. The current buy orders + the current position must be less than or equal to the buy limit
        # 2. The current sell orders + the current position must be greater than or equal to the sell limit
        
        # If the current position is already over the limit, return 0
        if buy:
            new_position = sum([order.quantity for order in self.my_orders if order.quantity > 0])
            return max(self.pos_limit - current_position - new_position, 0)
        else:
            new_position = sum([order.quantity for order in self.my_orders if order.quantity < 0])
            return min(-self.pos_limit - current_position - new_position, 0)

    def addLimitOrder(self, current_position: Position, buy: bool, quantity: int, price: int) -> Order:
        """
        Places a limit order at the given price and quantity, subject to the position limit. Checks the current
        positions and orders to ensure that the quantity does not exceed the maximum position limit for this symbol.
        
        Parameters:
        current_position (Position): The current position for this strategy's symbol.
        buy (bool): Whether the order is a buy or sell order. True for buy, False for sell.
        price (int): The price at which to place the order.
        quantity (int): The quantity of the order. Will be adjusted to fit within the position limit.

        Returns:
        (Order): The order that is to be placed.
        """
        
        max_new = self.maxNewPosition(current_position, buy)
        
        if buy:
            quantity = min(abs(quantity), abs(max_new))
        else:
            quantity = -min(abs(quantity), abs(max_new))

        new_order = Order(self.symbol, price, quantity)

        self.my_orders.append(new_order)
        return new_order

    def addMarketOrders(self, order_depth_after_mkt_orders: OrderDepth, current_position: Position,
        buy: bool, quantity: int) -> List[Order]:
        """
        Places a market order for the given quantity. Checks the current positions and orders to ensure that the
        quantity does not exceed the maximum position limit. Fills orders at the market price until either the quantity
        we  want to fill is filled, or there are no more orders to fill. removes the filled orders from our
        created order depth.

        Parameters:
        order_depth_after_mkt_orders (OrderDepth): The order depth after market orders have been filled.
        current_position (Position): The current position for this strategy's symbol.
        buy (bool): Whether the order is a buy or sell order. True for buy, False for sell.
        quantity (int): The quantity of the order.

        Returns:
        List[Order]: The list of market orders that are to be executed.
        """

        max_new = self.maxNewPosition(current_position, buy)
        
        quantity = min(abs(quantity), abs(max_new))

        # make sure the order depth is sorted
        sortOrderDepth(order_depth_after_mkt_orders)

        # we will go through the lowest sell orders for a buy, and the highest buy orders for a sell
        orders = None
        if buy:
            orders = order_depth_after_mkt_orders.sell_orders.copy()
        else:
            orders = order_depth_after_mkt_orders.buy_orders.copy()

        volume_filled = 0
        remaining_quantity = 0

        new_orders: List[Order] = []

        if quantity != 0:
            
            for price in orders:

                volume_filled += abs(orders[price])

                # Note: if there aren't enough orders to fill the quantity, we will fill as many as we can
                if volume_filled >= quantity:
                    remaining_quantity = quantity - (volume_filled - abs(orders[price]))

                    if buy:
                        new_orders.append(Order(self.symbol, price, abs(remaining_quantity)))
                    else:
                        new_orders.append(Order(self.symbol, price, -abs(remaining_quantity)))

                    if remaining_quantity == abs(orders[price]): # if the final order to be placed is the same size as the 
                        # matching order in the order book, we can just delete the order from the order book, otherwise, 
                        # we remove (from that order) the remaining quantity we need to fill
                        if buy:
                            del order_depth_after_mkt_orders.sell_orders[price]
                        else:
                            del order_depth_after_mkt_orders.buy_orders[price]
                    else:
                        if buy:
                            order_depth_after_mkt_orders.sell_orders[price] += remaining_quantity
                        else:
                            order_depth_after_mkt_orders.buy_orders[price] -= remaining_quantity
                    break
                else: # delete orders from our order book as we fill them

                    if buy:
                        new_orders.append(Order(self.symbol, price, abs(orders[price])))
                    else:
                        new_orders.append(Order(self.symbol, price, -abs(orders[price])))

                    if buy:
                        del order_depth_after_mkt_orders.sell_orders[price]
                    else:
                        del order_depth_after_mkt_orders.buy_orders[price]

        self.my_orders.extend(new_orders)

        return new_orders

def getMidPrice(state: TradingState, symbol: Symbol) -> float:
    Order_Depth = state.order_depths[symbol]
    Buy_Orders = Order_Depth.buy_orders
    max_bid = -1
    for key in Buy_Orders:
        if key > max_bid:
            max_bid = key

    min_ask = -1
    Sell_Orders = Order_Depth.sell_orders
    for key in Sell_Orders:
        if min_ask < 0:
            min_ask = key
            continue

        if key < min_ask:
            min_ask = key

    return float(max_bid + min_ask) / 2.0

# Get calculated fair price
def getFairPrice(self: Strategy, state: TradingState, max_bid: float, min_ask: float, look_back_period: int) -> float:
    if max_bid != -1:
        self.data['max_bids'].append(max_bid)
        if len(self.data['max_bids']) > look_back_period:
            self.data['max_bids'].pop(0)

    if min_ask != -1:
        self.data['min_asks'].append(min_ask)
        if len(self.data['min_asks']) > look_back_period:
            self.data['min_asks'].pop(0)

    if len(self.data['max_bids']) > 0:
        mb_avg = (sum(self.data['max_bids']) / len(self.data['max_bids']))
    else:
        mb_avg = -1

    if len(self.data['min_asks']) > 0:
        ms_avg = (sum(self.data['min_asks']) / len(self.data['min_asks']))
    else:
        ms_avg = -1

    if ms_avg >= 0 and mb_avg >= 0:
        base_price = (ms_avg + mb_avg) / 2.0
    else:
        base_price = -1

    return base_price

def DivingGearStrategy(self: Strategy, state: TradingState) -> None:
    self.data.setdefault("price_history", [])
    self.data.setdefault("bp_history", [])
    self.data.setdefault("bp_slope_history", [])
    self.data.setdefault('max_bids', [])
    self.data.setdefault('min_asks', [])
    self.data.setdefault('index_price_history', [])
    self.data.setdefault('dolphin_p_flux', [])
    self.data.setdefault('dolphin_p_flux_positive', False)
    self.data.setdefault('in_trade', False)
    self.data.setdefault('length_of_trade', 0)

    #PARAMS
    BASE_PRICE_SLOPE_LOOKBACK = 120
    BASE_PRICE_SLOPE_EXIT_THRESHOLD = 0.00001
    PFLUX_THRESHOLD = 5.0
    #ENDPARAMS

    self.data["price_history"].append(getMidPrice(state, self.symbol))
    self.data['index_price_history'].append(state.observations['DOLPHIN_SIGHTINGS'])
    if len(self.data['index_price_history']) > 1:
        self.data['dolphin_p_flux'].append(self.data['index_price_history'][-1] - self.data['index_price_history'][-2])
    else:
        self.data['dolphin_p_flux'].append(0)

    if self.symbol not in state.position:
        state.position[self.symbol] = 0

    max_bid = max(state.order_depths[self.symbol].buy_orders)
    min_ask = min(state.order_depths[self.symbol].sell_orders)

    base_price_for_slope = getFairPrice(self, state, max_bid, min_ask, BASE_PRICE_SLOPE_LOOKBACK)
    self.data['bp_history'].append(base_price_for_slope)
    if len(self.data['bp_history']) < BASE_PRICE_SLOPE_LOOKBACK:
        self.data['bp_slope_history'].append(0)
    else:
        self.data['bp_slope_history'].append(self.data['bp_history'][-1]/self.data['bp_history'][-BASE_PRICE_SLOPE_LOOKBACK] - 1)

    if abs(self.data['dolphin_p_flux'][-1]) > PFLUX_THRESHOLD and not self.data['in_trade']:
        self.data['in_trade'] = True
        if self.data['dolphin_p_flux'][-1] > 0:
            self.data['dolphin_p_flux_positive'] = True
        else:
            self.data['dolphin_p_flux_positive'] = False
        self.data['length_of_trade'] = 0

    elif self.data['in_trade'] and self.data['length_of_trade'] > BASE_PRICE_SLOPE_LOOKBACK and \
        (abs(self.data['bp_slope_history'][-1]) < BASE_PRICE_SLOPE_EXIT_THRESHOLD or \
        (self.data['dolphin_p_flux_positive'] and self.data['bp_slope_history'][-1] < 0) or \
        (not self.data['dolphin_p_flux_positive'] and self.data['bp_slope_history'][-1] > 0)):

        self.data['in_trade'] = False
        self.data['length_of_trade'] = 0

    best_ask = min(state.order_depths[self.symbol].sell_orders) if len(state.order_depths[self.symbol].sell_orders) > 0 else None
    best_bid = max(state.order_depths[self.symbol].buy_orders) if len(state.order_depths[self.symbol].buy_orders) > 0 else None

    if self.data['in_trade'] and self.data['dolphin_p_flux_positive']:
        self.data['length_of_trade'] += 1
        self.addLimitOrder(state.position[self.symbol], True, 999999, best_ask)
    elif self.data['in_trade'] and not self.data['dolphin_p_flux_positive']:
        self.data['length_of_trade'] += 1
        self.addLimitOrder(state.position[self.symbol], False, 999999, best_bid)

    else:
        if state.position[self.symbol] > 0:
            self.addLimitOrder(state.position[self.symbol], False, state.position[self.symbol], best_bid)
        else:
            self.addLimitOrder(state.position[self.symbol], True, state.position[self.symbol], best_ask)

# Strategies to run
strategies: List[Strategy] = [
    Strategy('DIVING_GEAR', limits['DIVING_GEAR'], DivingGearStrategy)
]

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
        
        result = {}
        
        global strategies
        for strategy in strategies:
            result[strategy.product] = strategy.run(state)
        
        return result