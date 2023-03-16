# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

import pandas
import numpy
import statistics
import math
import typing

from typing import Dict, List, Callable, Any
from datamodel import OrderDepth, TradingState, Order, Listing, Product, Symbol, Position

# Dictionaries for converting between products and symbols
products: Dict[Product, Symbol] = {}
symbols: Dict[Symbol, Product] = {}


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
        # Wiki is incorrect: Listing is a dict, not a class
        product = listings[symbol]['product']
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
    sorted_buy_orders = {i: order_depth.buy_orders[i] for i in buy_keys}

    sell_keys = list(order_depth.sell_orders.keys())
    sell_keys.sort()
    sorted_sell_orders = {i: order_depth.sell_orders[i] for i in sell_keys}

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
                remaining_volume = quantity - \
                    (volume - (-1 * sell_orders[price]))
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
        print("Price: " + str(price) + " Volume: " +
              str(order_depth.buy_orders[price]))

    print("Sell Orders:")
    for price in order_depth.sell_orders:
        print("Price: " + str(price) + " Volume: " +
              str(order_depth.sell_orders[price]))


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
        # A dictionary of data that persists across time steps
        self.data: Dict[Any, Any] = {}

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
            new_position = sum(
                [order.quantity for order in self.my_orders if order.quantity > 0])
            return max(self.pos_limit - current_position - new_position, 0)
        else:
            new_position = sum(
                [order.quantity for order in self.my_orders if order.quantity < 0])
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

        if buy:
            quantity = min(abs(quantity), abs(max_new))
        else:
            quantity = -min(abs(quantity), abs(max_new))

        # make sure the order depth is sorted
        sortOrderDepth(order_depth_after_mkt_orders)

        # we will go through the lowest sell orders for a buy, and the highest buy orders for a sell
        orders = None
        if buy:
            orders = order_depth_after_mkt_orders.sell_orders
        else:
            orders = order_depth_after_mkt_orders.buy_orders

        volume_filled = 0
        remaining_quantity = 0

        new_orders: List[Order] = []

        if quantity != 0:

            for price in orders:

                volume_filled += orders[price]

                # Note: if there aren't enough orders to fill the quantity, we will fill as many as we can
                if volume_filled >= quantity:
                    remaining_quantity = quantity - \
                        (volume_filled - orders[price])

                    new_orders.append(
                        Order(self.symbol, price, remaining_quantity))

                    # if the final order to be placed is the same size as the
                    if remaining_quantity == orders[price]:
                        # matching order in the order book, we can just delete the order from the order book, otherwise,
                        # we remove (from that order) the remaining quantity we need to fill
                        if buy:
                            del order_depth_after_mkt_orders.sell_orders[price]
                        else:
                            del order_depth_after_mkt_orders.buy_orders[price]
                    else:
                        if buy:
                            order_depth_after_mkt_orders.sell_orders[price] -= remaining_quantity
                        else:
                            order_depth_after_mkt_orders.buy_orders[price] -= remaining_quantity
                    break
                else:  # delete orders from our order book as we fill them

                    new_orders.append(Order(self.symbol, price, orders[price]))

                    if buy:
                        del order_depth_after_mkt_orders.sell_orders[price]
                    else:
                        del order_depth_after_mkt_orders.buy_orders[price]

        self.my_orders.extend(new_orders)

        return new_orders


def getMidPrice(state: TradingState) -> float:
    # print("State: ", state)
    Order_Depth = state.order_depths["BANANAS"]
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


def getQBoughtAndSold(state: TradingState) -> tuple[int, int]:
    Order_Depth = state.order_depths["BANANAS"]
    Buy_Orders = Order_Depth.buy_orders
    qb = 0
    for key in Buy_Orders:
        qb += Buy_Orders[key]

    Sell_Orders = Order_Depth.sell_orders
    qs = 0
    for key in Sell_Orders:
        qs += Sell_Orders[key]

    return qb, qs

# def bananaStrategy(self: Strategy, state: TradingState, base_price: int, spread: int, quantity: int, delay: int = 0,
#     hanging_orders: bool = False, ping_pong: bool = False) -> None:


def bananaStrategy(self: Strategy, state: TradingState) -> None:
    '''
    Strategy for Bananas utilizing the paper 
    ToDo:
    1. Write code to place orders (addLimitOrder)
    2. Consult with the other team on how to use their code
    3. Make it Modular
    4. Test it with base configuration (switch signs if needed)


    First Test:
    - Use Mid Price
    - HF_at = 0
    - Base_strat for deciding AP and BP
    - Inventory Skew (maxNewPosition) for quantities
    - Signs from paper (Switch signs if doesn't work)

    Hyperparameters (constants we will tune):
    - tick_size = 1.0
    - Activation_threshold(HF_at) = 0
    - Order_absorption_rate = 0.3 
    - ImbThresh = 0.5 
    - IncMult = 2
    - VolMult = 1

    '''

    if 'pt' not in self.data:
        self.data['pt'] = []

    # activation
    HF_at = 0
    Order_absorption_rate = 0.3
    ImbThresh = 0.5
    IncMult = 2
    tick_size = 1.0
    VolMult = 1

    current_pt = getMidPrice(state)
    if(len(self.data['pt']) < 2):
        self.data['pt'].append(current_pt)
        return

    pt1 = self.data['pt'][-1]
    pt2 = self.data['pt'][-2]

    p_flux = abs((pt1-pt2)/pt1)*10000

    if p_flux > HF_at:
        base_price = current_pt

        # base strat
        AP = base_price + tick_size
        BP = base_price - tick_size

        # # If using V high volatility. If high volatility market maker will place his orders deeper from standard situation
        # tick_size = 1.0
        # AP = base_price + (abs(current_pt - pt1)  + 1) * tick_size #changed + and -
        # BP = base_price - ( abs(current_pt - pt1)  + 1) * tick_size

        # #If using Imbalance Threshhold
        # qb, qs = getQBoughtAndSold(TradingState)

        # if (qb - qs)/ (qb + qs) > ImbThresh:
        #     AP = base_price + tick_size * IncMult #shouldn't ask price be minus?
        #     BP = base_price
        # elif (qs - qb)/(qb + qs) > ImbThresh:
        #     AP = base_price
        #     BP = base_price - tick_size * IncMult #Maybe +?
        # else:
        #     AP = base_price + tick_size #Maybe -??
        #     BP = base_price - tick_size #Maybe +??

        # #if using both
        # if (qb - qs)/ (qb + qs) > ImbThresh:
        #     AP = base_price + (abs(current_pt - pt1) + IncMult)*tick_size  #shouldn't ask price be minus?
        #     BP = base_price
        # elif (qs - qb)/(qb + qs) > ImbThresh:
        #     AP = base_price
        #     BP = base_price - (abs(current_pt - pt1) + IncMult)*tick_size #Maybe +?
        # else:
        #     AP = base_price - (abs(current_pt - pt1)  + 1) * tick_size
        #     BP = base_price + ( abs(current_pt - pt1)  + 1) * tick_size

        # # Base
        # AS = (((qb + qs)/2) * Order_absorption_rate)
        # BS = AS

        # Inventory Skew
        AS = Strategy.maxNewPosition(self, state.position, False)
        BS = Strategy.maxNewPosition(self, state.position, True)

        # addLimitOrder(self, current_position: Position, buy: bool, quantity: int, price: int) -> Order:
        self.addLimitOrder(self, state.position, False, AS, AP)
        self.addLimitOrder(self, state.position, True, BS, BP)

    # set new pt values
    self.data['pt'].append(current_pt)


# Strategies to run
strategies: List[Strategy] = [
    Strategy('BANANAS', 20, bananaStrategy)
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
