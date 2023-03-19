# Basic utilities for plotting and manipulating data

import math
import itertools
from typing import TypeVar, Dict, List, Tuple

# Add the top-level directory to the path to import the datamodel package
import sys
sys.path.append('../../')
from datamodel import Trade

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
    return {key : value * total / current_total for key, value in values.items()}

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
        s += "\t" + str(price_level) + ": " + str(distribution[price_level]) + ",\n"
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
    
    full_range = lambda: itertools.chain(range(buy_range[0], buy_range[1] + 1), range(sell_range[0], sell_range[1] + 1))
    price_counts: Dict[int, float] = {price : 0 for price in full_range()}
    price_volumes: Dict[int, float] = {price : 0 for price in full_range()}
    total_count: int = len(trades)
    total_volume: int = sum([trade.quantity for trade in trades])
    
    # Get the trades seperated by timestamp
    time_trades: Dict[int, List[Trade]] = {}
    
    for trade in trades:
        if trade.timestamp not in time_trades:
            time_trades[trade.timestamp] = []
            
        time_trades[trade.timestamp].append(trade)
    
    # Loop through each timestamp and count the trades/volume at each price level
    for timestamp, this_trades in time_trades.items():
        price = getMidPrice(this_trades)

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
    
    distribution: Dict[int, float] = {}
    
    # Calculation for distribution
    for price_level in full_range():
        
        # Edit this line using above data to calculate the distribution
        distribution[price_level] = price_volumes[price_level] # Calculate distribution using volume

    return distribution
