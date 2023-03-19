# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

import pandas
import numpy as np
import statistics
import math
import typing

from typing import Dict, List, Callable, Any, TypeVar
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
    values: Dict[T, int] = {p: math.floor(
        value * probabilities[p]) for p in probabilities}
    remaining = value - sum(value for value in values.values())

    # Sort the probabilities in descending order
    descending_keys = sorted(
        probabilities, key=lambda p: probabilities[p], reverse=True)

    # Distribute the remaining value into the lowest probability buckets
    for key in descending_keys:
        if remaining <= 0:
            break

        values[key] += 1  # Add one to the bucket
        remaining -= 1  # Subtract one from the remaining value

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
        # A dictionary of data that persists across time steps
        self.data: Dict[Any, Any] = {}
        self.Last_Price = 0
        self.EMA_short = 0
        self.EMA_long = 0

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


def getLastPrice(state: TradingState) -> float:
    if "BANANAS" in state.market_trades:
        Last_Price = state.market_trades["BANANAS"][0].price
        Last_time = state.market_trades["BANANAS"][0].timestamp

        for i in state.market_trades["BANANAS"]:
            if i.timestamp > Last_time:
                Last_Price = i.price

            elif i.timestamp == Last_time:

                Mid_Price = getMidPrice(state)

                if (i.price - Mid_Price) < Last_Price - Mid_Price:
                    Last_Price = i.price

    if "BANANAS" in state.own_trades:
        for i in state.own_trades["BANANAS"]:
            if i.timestamp > Last_time:
                Last_Price = i.price

            elif i.timestamp == Last_time:

                Mid_Price = getMidPrice(state)

                if (i.price - Mid_Price) < Last_Price - Mid_Price:
                    Last_Price = i.price

    if not "BANANAS" in state.market_trades and not "BANANAS" in state.own_trades:
        return None

    return Last_Price


def getBookQuantities(state: TradingState) -> tuple[int, int]:
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

# banana strategies


def basic_AP_BP(self: Strategy, state: TradingState, base_price: float, tick_size: float) -> tuple[int, int]:
    AP = base_price + tick_size
    BP = base_price - tick_size
    return [AP, BP]


def volatility(self: Strategy, state: TradingState, avg_price_change: float, base_price: float, tick_size: float) -> tuple[int, int]:
    AP = base_price + (abs(avg_price_change) + 1) * tick_size
    BP = base_price - (abs(avg_price_change) + 1) * tick_size
    return [AP, BP]


def imbalance(self: Strategy, state: TradingState, qb: int, qs: int, base_price: float, tick_size: float, ImbThresh: float, IncMult: float) -> tuple[int, int]:
    if (qb + qs) != 0 and (qb - qs) / (qb + qs) > ImbThresh:
        AP = base_price + tick_size * IncMult  # shouldn't ask price be minus?
        BP = base_price
    elif (qb + qs) != 0 and (qs - qb)/(qb + qs) > ImbThresh:
        AP = base_price
        BP = base_price - tick_size * IncMult  # Maybe +?
    else:
        AP = base_price + tick_size  # Maybe -??
        BP = base_price - tick_size  # Maybe +??
    return [AP, BP]


def imb_vol(self: Strategy, state: TradingState, avg_price_change: float, qb: int, qs: int, base_price: float, tick_size: float, ImbThresh: float, IncMult: float) -> tuple[int, int]:
    if (qb + qs) != 0 and (qb - qs) / (qb + qs) > ImbThresh:
        AP = base_price + (abs(avg_price_change) + IncMult) * \
            tick_size  # shouldn't ask price be minus?
        BP = base_price
    elif (qb + qs) != 0 and (qs - qb)/(qb + qs) > ImbThresh:
        AP = base_price
        BP = base_price - (abs(avg_price_change) + IncMult) * \
            tick_size  # Maybe +?
    else:
        AP = base_price - (abs(avg_price_change) + 1) * tick_size
        BP = base_price + (abs(avg_price_change) + 1) * tick_size
    return [AP, BP]


def basic_AS_BS(self: Strategy, state: TradingState, qb: int, qs: int, Order_absorption_rate: float) -> tuple[int, int]:
    AS, BS = inventory_skew(self, state)
    if ((((qb + qs)/2) * Order_absorption_rate) <= min(AS, BS)):
        AS = BS = (((qb + qs)/2) * Order_absorption_rate)
    else:
        AS = BS = min(AS, BS)
    return [AS, BS]


def inventory_skew(self: Strategy, state: TradingState) -> tuple[int, int]:
    if "BANANAS" not in state.position:
        state_pos = 0
    else:
        state_pos = state.position['BANANAS']

    AS = Strategy.maxNewPosition(self, state_pos, False)
    BS = Strategy.maxNewPosition(self, state_pos, True)
    return [AS, BS]


def get_APBP(self: Strategy, state: TradingState, qb: int, qs: int, base_price: float,
             tick_size: float, EMA_Thresh: float, IncMult: float) -> float:

    if self.EMA > EMA_Thresh:
        AP = base_price + tick_size * IncMult  # shouldn't ask price be minus?
        BP = base_price
    elif self.EMA < -1 * EMA_Thresh:
        AP = base_price
        BP = base_price - tick_size * IncMult  # Maybe +?
    else:
        AP = base_price + tick_size  # Maybe -??
        BP = base_price - tick_size  # Maybe +??

    return [AP, BP]


def get_EMA(self: Strategy, state: TradingState, L: float, EMA: float) -> float:
    '''
    Function returns the current EMA
    if EMA == 0:
        set EMA to last midprice
    else:
        EMA = e^(-L) * EMA + (1 - e^(-L)) * Current_Mid_Price
    '''
    L_use = (1.0/L)
    if EMA == 0:
        EMA = self.data['mp'][-1]
    else:
        # prev = self.EMA_short
        EMA = math.exp(-L_use)*EMA + (1-math.exp(-L_use))*self.data['mp'][-1]

    return EMA


def change_Spread(self: Strategy, state: TradingState, cross_over: float,
                  bid_prices: List[int], ask_prices: List[int]) -> None:
    '''
    Returns the ask price and bid price

    Pseudocode: 
    - pass in a list of current bid prices and ask prices
    - Based on cross-over, we decide which to mess with

    if cross_over > 0:
        mess with ask prices
    elif cross_over < 0:
        mess with bid prices
    '''
    mp = self.data['mp'][-1]

    if cross_over > 0:
        for i, price in enumerate(ask_prices):
            ask_prices[i] = (mp + (price - mp) * 2)
    elif cross_over < 0:
        for i, price in enumerate(bid_prices):
            bid_prices[i] = max((mp - (mp - price) * 2), 1)


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

    if 'mp' not in self.data:
        self.data['mp'] = []

    # activation
    lookback_period = 10  # if less than 10 do as far back as possible
    L_short = 12.0
    L_long = 96.0
    EMA_Thresh = 0.0
    tick_size = 1.0
    HF_at = -1
    Order_absorption_rate = 1.0
    ImbThresh = 0.5
    IncMult = 2
    VolMult = 1
    qb, qs = getBookQuantities(state)
    # use last price if no last price use mid price.
    '''
    if i set it to last price then ... 
    option1:
    always trade of last price
    always trade of mid price
    if no last price trade of mid price
    
    should the function return the last traded price regardless of wether it was in this time step or not

    no we should keep a gloabl last price 
    funciton should try and grab the price from this iteration if not then it returns null.
    '''
    current_pt = getMidPrice(state)
    self.data['mp'].append(current_pt)
    if(len(self.data['mp']) == 1):
        return

    # Updates the EMA
    self.EMA_short = get_EMA(self, state, L_short, self.EMA_short)
    self.EMA_long = get_EMA(self, state, L_long, self.EMA_long)
    cross_over = self.EMA_short - self.EMA_long

    #self.EMA_short = get_EMA(self, state, L_short, self.EMA_short)
    # pt1 = self.data['mp'][-1]
    # pt2 = self.data['mp'][-2]

    # update EMA

    if self.EMA_short == 0:
        self.EMA_short = self.data['mp'][-1]
    else:
        # prev = self.EMA_short
        self.EMA_short = math.exp(-L_short)*self.EMA_short + \
            (1-math.exp(-L_short))*self.data['mp'][-1]

    if self.EMA_long == 0:
        self.EMA_long = self.data['mp'][-1]
    else:
        self.EMA_long = math.exp(-L_long)*self.EMA_long + \
            (1-math.exp(-L_long))*self.data['mp'][-1]

    # Update average change in price
    lim = 0
    if len(self.data['mp']) < lookback_period:
        lim = len(self.data['mp'])
    else:
        lim = lookback_period

    temp_data = self.data['mp'][-lim:]
    avg = 0
    for x in range(0, len(temp_data)-1):
        avg += abs(temp_data[x]-temp_data[x+1])

    avg /= lim
    avg_price_change = avg
    vol = statistics.stdev(self.data['mp'][-lim:])*math.sqrt(lim)

    print("size of self.data[pt]: ", len(self.data["pt"]))
    print("avg_price: ", avg_price_change)
    print("qs and qb avg: ", (qs+qb)/2.0)
    AS, BS = inventory_skew(self, state)
    print("AS: ", AS)
    print("BS: ", BS)
    print("EMA: ", self.EMA_short)

    if vol > HF_at:
        base_price = current_pt

        '''
        #Base Price is always last price
        if getLastPrice(state) == None:
            #base_price = getMidPrice(state) # uncomment if you want base price to be mid when there is no last price
            base_price = self.Last_Price
        else:
            base_price = self.Last_Price = getLastPrice(state)
        '''
        # basic strategy APBP
        #APBP_vals = basic_AP_BP(self, state, base_price, tick_size)

        # volatility strategy
        #APBP_vals = volatility(self, state, avg_price_change, base_price, tick_size)

        # imbalance strategy
        #APBP_vals = imbalance(self, state, qb, qs, base_price, tick_size, ImbThresh, IncMult)

        # EMA Strategy
        APBP_vals = get_APBP(self, state, qb, qs, base_price,
                             tick_size, EMA_Thresh, IncMult)

        # both strategy
        #APBP_vals = imb_vol(self, state, avg_price_change, qb, qs, base_price, tick_size, ImbThresh, IncMult)

        # basic strategy for ASBS
        #ASBS_vals = basic_AS_BS(self, state, qb, qs, Order_absorption_rate)

        # inventory skew
        ASBS_vals = inventory_skew(self, state)

        if "BANANAS" not in state.position:
            state_pos = 0
        else:
            state_pos = state.position['BANANAS']

        print("state_pos: ", state_pos)
        print("---------------------------------------")

        # addLimitOrder(self, current_position: Position, buy: bool, quantity: int, price: int) -> Order:
        #AP, BP, AS, BS
        self.addLimitOrder(state_pos, False, ASBS_vals[0], APBP_vals[0])
        self.addLimitOrder(state_pos, True, ASBS_vals[1], APBP_vals[1])

    # set new pt values
    self.data['mp'].append(current_pt)


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
