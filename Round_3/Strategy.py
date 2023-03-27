# Combined Strategy for Bananas and Pearls

import math
from numpy import corrcoef
import json

from typing import Dict, List, Callable, Any, TypeVar
from datamodel import OrderDepth, TradingState, Order, Listing, Product, Symbol, Position, ProsperityEncoder

# Dictionaries for converting between products and symbols
products: Dict[Product, Symbol] = {}
symbols: Dict[Symbol, Product] = {}

# Must be hard-coded, not accessible via TradingState. IMC will publish this
# information before each round, update here accordingly.
limits: Dict[Symbol, int] = {
    'PEARLS': 20,
    'BANANAS': 20,
}

# hard coded frequency distribution for pearls based on the amount of volume traded at that price level
pearl_distribution: Dict[int,float] = {
    9995: 0.20427428871115774,
    9996: 0.2702242034876098,
    9997: 0.0,
    9998: 0.5255015078012325,
    9999: 0.0,
    10001: 0.0,
    10002: 0.5271338603778641,
    10003: 0.0,
    10004: 0.27026664880075035,
    10005: 0.2025994908213855,
}

banana_distribution: Dict[int, float] = {
    -1: 1,
    1: 1
}

Coco_distribution: Dict[int, float] = {
        -6: 0.06410549584571995,
        -5: 0.14696242091622838,
        -4: 0.22478847473130573,
        -3: 0.24430215717661408,
        -2: 0.16662855400564067,
        -1: 0.13110755392941534,
        1: 0.16736401673640167,
        2: 0.20678754067875407,
        3: 0.24490934449093446,
        4: 0.198326359832636,
        5: 0.1196652719665272,
        6: 0.04797768479776848,
}

pina_distribution: Dict[int, float] = {
        -6: 0.06410549584571995,
        -5: 0.14696242091622838,
        -4: 0.22478847473130573,
        -3: 0.24430215717661408,
        -2: 0.16662855400564067,
        -1: 0.13110755392941534,
        1: 0.16736401673640167,
        2: 0.20678754067875407,
        3: 0.24490934449093446,
        4: 0.198326359832636,
        5: 0.1196652719665272,
        6: 0.04797768479776848,
}

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""

logger = Logger()

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

    # print("Buy Orders:")
    for price in order_depth.buy_orders:
        # print("Price: " + str(price) + " Volume: " + str(order_depth.buy_orders[price]))
        continue
    
    # print("Sell Orders:")
    for price in order_depth.sell_orders:
        # print("Price: " + str(price) + " Volume: " + str(order_depth.sell_orders[price]))
        continue
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
                        # print("Placing order for", abs(remaining_quantity), "shares at", price, "for", self.symbol)
                    else:
                        new_orders.append(Order(self.symbol, price, -abs(remaining_quantity)))
                        # print("Placing order for", -abs(remaining_quantity), "shares at", price, "for", self.symbol)

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
                        # print("Placing order for", abs(orders[price]), "shares at", price, "for", self.symbol)
                    else:
                        new_orders.append(Order(self.symbol, price, -abs(orders[price])))
                        # print("Placing order for", -abs(orders[price]), "shares at", price, "for", self.symbol)

                    if buy:
                        del order_depth_after_mkt_orders.sell_orders[price]
                    else:
                        del order_depth_after_mkt_orders.buy_orders[price]

        self.my_orders.extend(new_orders)

        return new_orders

def add_EMA(self: Strategy, state: TradingState, L: float, EMA: list[float]):
    '''
    Function returns the current EMA
    if EMA == 0:
        set EMA to last midprice
    else:
        EMA = e^(-L) * EMA + (1 - e^(-L)) * Current_Mid_Price
    '''
    L_use = (1.0/L)
    if len(EMA) == 0:
        EMA.append(self.data['price_history'][-1])
    else:
        # prev = self.EMA_short
        EMA.append(math.exp(-L_use)*EMA[-1] + (1-math.exp(-L_use))*self.data['price_history'][-1])

def get_EMA_slope(self: Strategy, state: TradingState, L: int) -> float:
    '''
    Function returns the slope of the EMA
    '''
    EMA = self.data['ema_long']

    if len(EMA) < L:
        return 0
    else:
        return (EMA[-1] - EMA[-L])/L

def getMidPrice(self: Strategy, state: TradingState) -> float:
    Order_Depth = state.order_depths[self.symbol]
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

def market_making_pearls_strategy(self: Strategy, state: TradingState) -> None:
    global pearl_distribution

    if self.symbol not in state.position:
        state.position[self.symbol] = 0

    max_buy = self.maxNewPosition(state.position[self.symbol], True)
    max_sell = self.maxNewPosition(state.position[self.symbol], False)
    
    buy_orders = distributeValue(max_buy, {price: pearl_distribution[price] for price in range(9999, 9994, -1)})
    sell_orders = distributeValue(abs(max_sell), {price: pearl_distribution[price] for price in range(10001, 10006)})
    sell_orders = {price: -sell_orders[price] for price in sell_orders}
    
    for price in buy_orders:
        if buy_orders[price] > 0:
            self.addLimitOrder(state.position[self.symbol], True, buy_orders[price], price)
    for price in sell_orders:
        if sell_orders[price] < 0:
            self.addLimitOrder(state.position[self.symbol], False, sell_orders[price], price)

# def getVolatility(state: TradingState, self: Strategy) -> float:
#     prices = self.data['price_history']
#     avg = (float(sum(prices))/len(prices))

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

def BananaStrategy(self: Strategy, state: TradingState) -> None:
    global banana_distribution
    self.data.setdefault('max_bids', [])
    self.data.setdefault('min_asks', [])
    
    if self.symbol not in state.position:
        state.position[self.symbol] = 0

    max_buy = self.maxNewPosition(state.position[self.symbol], True)
    max_sell = self.maxNewPosition(state.position[self.symbol], False)
 
    max_bid = max(state.order_depths[self.symbol].buy_orders)
    min_ask = min(state.order_depths[self.symbol].sell_orders)

    base_price = int(round((getFairPrice(self, state, max_bid, min_ask, 7)), 0))

    offset_banana_distribution = {price + base_price: banana_distribution[price] for price in banana_distribution}

    buy_orders = distributeValue(max_buy, {price: offset_banana_distribution[price] for price in range(base_price-1, base_price-2, -1)})
    sell_orders = distributeValue(abs(max_sell), {price: offset_banana_distribution[price] for price in range(base_price+1, base_price+2)})
    sell_orders = {price: -sell_orders[price] for price in sell_orders}
        
    sell_order_prices = [price for price in sell_orders]
    buy_order_prices = [price for price in buy_orders]

    buy_order_volumes = [buy_orders[price] for price in buy_orders]
    sell_order_volumes = [sell_orders[price] for price in sell_orders]

    buy_orders = {price: buy_order_volumes[i] for i, price in enumerate(buy_order_prices)}
    sell_orders = {price: sell_order_volumes[i] for i, price in enumerate(sell_order_prices)}

    for price in buy_orders:
        if buy_orders[price] > 0:
            self.addLimitOrder(state.position[self.symbol], True, buy_orders[price], price)
    for price in sell_orders:
        if sell_orders[price] < 0:
            self.addLimitOrder(state.position[self.symbol], False, sell_orders[price], price)

def CocoStrategy(self: Strategy, state: TradingState) -> None:
    global Coco_distribution

    self.data.setdefault("price_history", [])
    self.data.setdefault("bp_history", [])
    self.data.setdefault('ema_short', [])
    self.data.setdefault('ema_long', [])
    self.data.setdefault('max_bids', [])
    self.data.setdefault('min_asks', [])

    self.data["price_history"].append(getMidPrice(self, state))
    add_EMA(self, state, 4.0, self.data['ema_short'])
    add_EMA(self, state, 96.0, self.data['ema_long'])

    if self.symbol not in state.position:
        state.position[self.symbol] = 0

    max_buy = self.maxNewPosition(state.position[self.symbol], True)
    max_sell = self.maxNewPosition(state.position[self.symbol], False)

    max_bid = max(state.order_depths[self.symbol].buy_orders)
    min_ask = min(state.order_depths[self.symbol].sell_orders)

    base_price = int(round((getFairPrice(self, state, max_bid, min_ask, 4)), 0))
    # base_price = int(round(self.data['ema_short'][-1]), 0)
    base_price_raw = getFairPrice(self, state, max_bid, min_ask, 4)
    self.data['bp_history'].append(base_price_raw)
    ask_price = base_price + 1
    bid_price = base_price - 1

    offset_Coco_distribution = {price + base_price: Coco_distribution[price] for price in Coco_distribution}

    buy_orders = distributeValue(max_buy, {price: offset_Coco_distribution[price] for price in range(base_price-1, base_price-7, -1)})
    sell_orders = distributeValue(abs(max_sell), {price: offset_Coco_distribution[price] for price in range(base_price+1, base_price+7)})
    sell_orders = {price: -sell_orders[price] for price in sell_orders}
        
    sell_order_prices = [price for price in sell_orders]
    buy_order_prices = [price for price in buy_orders]

    buy_order_volumes = [buy_orders[price] for price in buy_orders]
    sell_order_volumes = [sell_orders[price] for price in sell_orders]

    buy_orders = {price: buy_order_volumes[i] for i, price in enumerate(buy_order_prices)}
    sell_orders = {price: sell_order_volumes[i] for i, price in enumerate(sell_order_prices)}
        
    ask_offset = 0
    bid_offset = 0
   
    # highest_bid = max(state.order_depths[self.symbol].buy_orders.keys()) 
    # lowest_ask = min(state.order_depths[self.symbol].sell_orders.keys())

    # our_highest_bid = max(buy_orders.keys()) + bid_offset
    # our_lowest_ask = min(sell_orders.keys()) + ask_offset


    # print(str(highest_bid) + " " + str(lowest_ask) + " " + str(our_lowest_ask) + " " + str(our_highest_bid) + " " + str(base_price) + " " + str(slope))
    # print(base_price)
    # mid_price = (highest_bid + lowest_ask) / 2.0
    # print(mid_price)
    
    for price in buy_orders:
        if buy_orders[price] > 0:
            self.addLimitOrder(state.position[self.symbol], True, buy_orders[price], bid_price + bid_offset)
    for price in sell_orders:
        if sell_orders[price] < 0:
            self.addLimitOrder(state.position[self.symbol], False, sell_orders[price], ask_price + ask_offset)

def add_MACD(self: Strategy, state: TradingState, L: float, MACD: list[float], MACD_signal: list[float]):
    '''
    Function returns the current MACD and MACD_signal
    MACD = EMA_short - EMA_long
    MACD_signal = e^(-L) * MACD_signal + (1 - e^(-L)) * MACD
    '''
    L_use = (1.0/L)
    MACD.append(self.data['ema_short'][-1] - self.data['ema_long'][-1])
    if len(MACD_signal) == 0:
        MACD_signal.append(MACD[-1])
    else:
        MACD_signal.append(math.exp(-L_use)*MACD_signal[-1] + (1-math.exp(-L_use))*MACD[-1])

def getMidPriceTS(state: TradingState, symbol: Symbol) -> float:
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

# The pairs trading strategy will also take in a symbol for the correlating product
def pairsTradingStrategy(self: Strategy, state: TradingState, correlating_symbol: Symbol) -> None:
    if self.symbol not in state.position:
        state.position[self.symbol] = 0
        
    order_depth_after_mkt_orders = state.order_depths[self.symbol]

    self.data.setdefault("price_history", [])
    self.data.setdefault("correlating_product_price_history", [])
    self.data.setdefault("correlation_hist", [])
    self.data.setdefault("in_trade", False)
    self.data.setdefault('sloping', False)
    self.data.setdefault('max_bids', [])
    self.data.setdefault('min_asks', [])
    self.data.setdefault('bp_history', [])
    self.data.setdefault('ema_short', [])
    self.data.setdefault('ema_long', [])
    self.data.setdefault('macd', [])
    self.data.setdefault('macd_signal', [])

    self.data['price_history'].append(getMidPriceTS(state, self.symbol))
    self.data['correlating_product_price_history'].append(getMidPriceTS(state, correlating_symbol))

    add_EMA(self, state, 12, self.data['ema_short'])
    add_EMA(self, state, 26, self.data['ema_long'])
    add_MACD(self, state, 9, self.data['macd'], self.data['macd_signal'])

    CORRELATION_LOOKBACK = 26

    correlation = corrcoef(self.data['price_history'][-CORRELATION_LOOKBACK:-1], self.data['correlating_product_price_history'][-CORRELATION_LOOKBACK:-1])[0, 1] if len(self.data['price_history']) >= CORRELATION_LOOKBACK else 0
    
    self.data["correlation_hist"].append(correlation)
    
    max_bid = max(state.order_depths[self.symbol].buy_orders)
    min_ask = min(state.order_depths[self.symbol].sell_orders)

    base_price = int(round((getFairPrice(self, state, max_bid, min_ask, 4)), 0))
    base_price_raw = getFairPrice(self, state, max_bid, min_ask, 4)
    self.data['bp_history'].append(base_price_raw)

    ask_price = base_price + 3
    bid_price = base_price - 3
    UPPER_CORR_THRESHOLD = 0.7
    LOWER_CORR_THRESHOLD = 0.1


    SLOPE_THRESH = 1.3
    SLOPE_LOOKBACK = 6
    STOP_THRESH = 1.0
    

    lim = 0
    if len(self.data['price_history']) < SLOPE_LOOKBACK:
        lim = len(self.data['price_history'])
    else:
        lim = SLOPE_LOOKBACK

    temp_data = self.data['price_history'][-lim:]
    avg = 0
    for x in range(0, len(temp_data)-1):
        avg += temp_data[x+1]-temp_data[x]

    avg /= lim
    slope = avg

    if correlation != 0:
        if correlation < LOWER_CORR_THRESHOLD:            
            if self.data['price_history'][-1] > 1.875 * self.data['correlating_product_price_history'][-1]:
                bid_price = bid_price - 1
                ask_price = ask_price - 1
            else:
                ask_price = ask_price + 1
                bid_price = bid_price + 1
            self.data["in_trade"] = True          
        elif self.data['in_trade']:
            if correlation < UPPER_CORR_THRESHOLD:
                if self.data['price_history'][-1] > 1.875 * self.data['correlating_product_price_history'][-1]:
                    bid_price = bid_price - 1
                    ask_price = ask_price - 1
                else:
                    bid_price = bid_price + 1
                    ask_price = ask_price + 1
            else:
                self.data['in_trade'] = False

        self.addLimitOrder(state.position[self.symbol], True, 9999999, bid_price)
        self.addLimitOrder(state.position[self.symbol], False, 9999999, ask_price)

def BerryStrategy(self: Strategy, state: TradingState) -> None:
    if self.symbol not in state.position:
        state.position[self.symbol] = 0
    
    lowest_ask = min(state.order_depths[self.symbol].sell_orders) if len(state.order_depths[self.symbol].sell_orders) > 0 else 0
    highest_bid = max(state.order_depths[self.symbol].buy_orders) if len(state.order_depths[self.symbol].buy_orders) > 0 else 0
            
    if (state.timestamp % 1000000 > 350000 and state.timestamp % 1000000 < 500000):
        if lowest_ask > 0:
            self.addLimitOrder(state.position[self.symbol], True, 100, lowest_ask)
    elif (state.timestamp % 1000000 > 500000 and state.timestamp % 1000000 < 700000):
        if highest_bid > 0:
            self.addLimitOrder(state.position[self.symbol], False, 100, highest_bid)
    else:  
        if lowest_ask > 0 and state.position[self.symbol] < 0:
            self.addLimitOrder(state.position[self.symbol], True, -state.position[self.symbol], lowest_ask)
        elif highest_bid > 0 and state.position[self.symbol] > 0:
            self.addLimitOrder(state.position[self.symbol], False, state.position[self.symbol], highest_bid)  
    
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

    self.data["price_history"].append(getMidPrice(self, state))
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
        
        if best_ask is not None:
            self.addLimitOrder(state.position[self.symbol], True, 999999, best_ask)
    elif self.data['in_trade'] and not self.data['dolphin_p_flux_positive']:
        self.data['length_of_trade'] += 1
        
        if best_bid is not None:
            self.addLimitOrder(state.position[self.symbol], False, 999999, best_bid)

    else:
        if state.position[self.symbol] > 0 and best_bid is not None:
            self.addLimitOrder(state.position[self.symbol], False, state.position[self.symbol], best_bid)
        elif best_ask is not None:
            self.addLimitOrder(state.position[self.symbol], True, state.position[self.symbol], best_ask)


# Strategies to run
strategies: List[Strategy] = [
    Strategy('PEARLS', limits["PEARLS"], market_making_pearls_strategy),
    Strategy('BANANAS', limits["BANANAS"], BananaStrategy),
    Strategy("COCONUTS", 600, CocoStrategy),
    # Strategy("COCONUTS", 300, lambda self, state: pairsTradingStrategy(self, state, "PINA_COLADAS")),
	Strategy("PINA_COLADAS", 300, lambda self, state: pairsTradingStrategy(self, state, "COCONUTS")),
    Strategy("BERRIES", 250, BerryStrategy),
    Strategy("DIVING_GEAR", 50, DivingGearStrategy),
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
            
        pina_listings = {"PINA_COLADAS": state.listings["PINA_COLADAS"]} if "PINA_COLADAS" in state.listings else {}
        pina_od = {"PINA_COLADAS": state.order_depths["PINA_COLADAS"]} if "PINA_COLADAS" in state.order_depths else {}
        pina_own = {"PINA_COLADAS": state.own_trades["PINA_COLADAS"]} if "PINA_COLADAS" in state.own_trades else {}
        pina_mkt = {"PINA_COLADAS": state.market_trades["PINA_COLADAS"]} if "PINA_COLADAS" in state.market_trades else {}
        pina_position = {"PINA_COLADAS": state.position["PINA_COLADAS"]} if "PINA_COLADAS" in state.position else {}
        pina_observations = {"PINA_COLADAS": state.observations["PINA_COLADAS"]} if "PINA_COLADAS" in state.observations else {}
        
        pina_state = TradingState(state.timestamp, pina_listings, pina_od, pina_own, pina_mkt, pina_position, pina_observations)

        logger.flush(pina_state,result)

        return result