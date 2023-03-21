# Basic utilities for plotting and manipulating data

import math
import itertools
from typing import TypeVar, Dict, List, Tuple

# Add the top-level directory to the path to import the datamodel package
import sys
sys.path.append('../')
from datamodel import Trade, Order, Product, Time, Symbol, UserId

T = TypeVar('T')


def normalizeTo(values: Dict[T, float], total: float) -> Dict[T, float]:
    """
    Normalizes the given values to the given total. Takes in a dictionary of anything corresponding to a float,
    and returns a new dictionary with the same keys and the values normalized to the given total.

    Parameters:
    values: The values to normalize
    total: The total to normalize to

    Returns:
    The normalized values dictionary
    """
    current_total = sum(values.values())
    return {key: value * total / current_total for key, value in values.items()}


def distributionToStr(distribution: Dict[int, float]) -> str:
    """
    Converts a distribution dictionary to a string. The distribution dictionary is a dictionary of price levels
    corresponding to the desired distribution of values at that level.

    Parameters:
    distribution: The distribution dictionary to convert to a string

    Returns:
    A string representation of the distribution dictionary
    """

    s: str = "distribution: Dict[int, float] = {\n"
    for price_level in sorted(distribution.keys()):
        s += "\t" + str(price_level) + ": " + \
            str(distribution[price_level]) + ",\n"
    s += "}\n"
    return s


def getMidPrice(trades: List[Trade]) -> float:
    """
    Calculates the mid price of the given trades. The mid price is the average of the highest and lowest prices.

    Parameters:
    trades (List[Trade]): The trades to calculate the mid price of

    Returns:
    float: The mid price of the given trades
    """

    highest = max(trade.price for trade in trades)
    lowest = min(trade.price for trade in trades)
    return (highest + lowest) / 2


def calcDynamicMMDistribution(trades: List[Trade], buy_range: Tuple[int, int],
                              sell_range: Tuple[int, int]) -> Dict[int, float]:
    """
    Calculate a price level distribution based on the trades at each price level. The price level is not constant,
    but is determined by some calculation. Instead of working with price levels (9998, 9999, 10001, etc.) we
    work with price differences (-2, -1, 1, etc.).

    Parameters:
    trades (List[Trade]): A list of trades to calculate the distribution from
    buy_range (Tuple[int, int]): The range of price differences to consider as buy trades
    sell_range (Tuple[int, int]): The range of price differences to consider as sell trades

    Returns:
    Dict[int, float]: A dictionary mapping price differences to the values of the distribution at that level
    """

    def full_range(): return itertools.chain(
        range(buy_range[0], buy_range[1] + 1), range(sell_range[0], sell_range[1] + 1))
    price_counts: Dict[int, float] = {price: 0 for price in full_range()}
    price_volumes: Dict[int, float] = {price: 0 for price in full_range()}
    total_count: int = len(trades)
    total_volume: int = sum([trade.quantity for trade in trades])

    # Get the trades seperated by timestamp
    time_trades: Dict[int, List[Trade]] = {}

    for trade in trades:
        if trade.timestamp not in time_trades:
            time_trades[trade.timestamp] = []

        time_trades[trade.timestamp].append(trade)

    # Loop through each timestamp and count the trades/volume at each price level
    price = getMidPrice(this_trades)
    for timestamp, this_trades in time_trades.items():
        for trade in this_trades:
            # Calculate the price difference
            price_diff = trade.price - price

            if price_diff > 0:
                price_diff = math.ceil(price_diff)
            else:
                price_diff = math.floor(price_diff)

            # Add the trade to the price counts and volumes
            price_counts.setdefault(price_diff, 0)
            price_counts[price_diff] += 1
            price_volumes.setdefault(price_diff, 0)
            price_volumes[price_diff] += trade.quantity

        price = getMidPrice(this_trades)

    distribution: Dict[int, float] = {}

    # Calculation for distribution
    for price_level in full_range():

        # Edit this line using above data to calculate the distribution
        # Calculate distribution using volume
        distribution[price_level] = price_volumes[price_level]

    return distribution

def csvToDict(file_name: str) -> Dict[str, List[str]]:
    """
    Parse a csv file and return a dictionary mapping column names to a list of values in that column.
    
    Parameters:
    file_name (str): The name of the file to parse
    
    Returns:
    Dict[str, List[str]]: A dictionary mapping column names to a list of values in that column
    """
    # A mapping of products to columns, which are a mapping of column names to a list of values
    data_dict: Dict[str, List[str]] = {}
    titles: List[str] = []

    # Open the file
    with open(file_name, "r") as f:
        lines = f.readlines()
        titles = lines.pop(0).strip().split(",")
        
        for line in lines:
            line = line.strip().split(",")
            assert len(line) == len(titles)

            for c, column in enumerate(line):
                data_dict.setdefault(titles[c], [])
                data_dict[titles[c]].append(column)
                
    return data_dict
    

def parseCombinedLOB(file_name: str) -> Dict[Product, Dict[Time, Tuple[List[Order], float, float]]]:
    """
    Parses the combined LOB file and returns a dictionary mapping products to a dictionary mapping timestamps to a tuple
    of a list of orders and the mid price and profit and loss at that timestamp.
    
    Parameters:
    file_name (str): The name of the file to parse

    Returns:
    A dictionary mapping products to a dictionary mapping timestamps to a tuple
    of a list of orders and the mid price and profit and loss at that timestamp.
    """
    
    data_dict = csvToDict(file_name)    
    line_count = len(data_dict["timestamp"])
    all_data: Dict[Product, Dict[Time, Tuple[List[Order], float, float]]] = {}

    # Parse the lines
    for line_num in range(line_count):
        timestamp: Time = int(float(data_dict["timestamp"][line_num]))
        product: Product = data_dict["product"][line_num]
        mid_price: float = float(data_dict["mid_price"][line_num])
        profit_and_loss: float = float(data_dict["profit_and_loss"][line_num])
        orders: List[Order] = []

        for order_num in range(1, 4):
            bid_price = data_dict["bid_price_" + str(order_num)][line_num]
            bid_volume = data_dict["bid_volume_" + str(order_num)][line_num]
            ask_price = data_dict["ask_price_" + str(order_num)][line_num]
            ask_volume = data_dict["ask_volume_" + str(order_num)][line_num]
            
            if bid_price != "" and bid_volume != "":
                bid_price = int(float(bid_price))
                bid_volume = int(float(bid_volume))
                bid_order = Order(product, bid_price, bid_volume)
                orders.append(bid_order)
                
            if ask_price != "" and ask_volume != "":
                ask_price = int(float(ask_price))
                ask_volume = int(float(ask_volume))
                ask_order = Order(product, ask_price, ask_volume)
                orders.append(ask_order)
                
        all_data.setdefault(product, {})
        all_data[product][timestamp] = (orders, mid_price, profit_and_loss)

    return all_data

def parseCombinedTrades(file_name: str) -> Dict[Symbol, List[Trade]]:
    """
    Parses the combined trades file and returns a dictionary mapping symbols to a list of trades.
    
    Parameters:
    file_name (str): The name of the file to parse
    
    Returns:
    Dict[Symbol, List[Trade]]: A dictionary mapping symbols to a list of trades
    """
    data_dict = csvToDict(file_name)
    line_count = len(data_dict["timestamp"])
    trades: Dict[Product, List[Trade]] = {}
    
    for line_num in range(line_count):
        timestamp: Time = int(float(data_dict["timestamp"][line_num]))
        buyer: UserId = data_dict["buyer"][line_num]
        seller: UserId = data_dict["seller"][line_num]
        symbol: Symbol = data_dict["symbol"][line_num]
        currency: Symbol = data_dict["currency"][line_num]
        price: int = int(float(data_dict["price"][line_num]))
        quantity: int = int(float(data_dict["quantity"][line_num]))
        trade = Trade(symbol, price, quantity, buyer, seller, timestamp)
        trades.setdefault(symbol, [])
        trades[symbol].append(trade)

    return trades
