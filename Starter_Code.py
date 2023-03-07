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
from datamodel import OrderDepth, TradingState, Order, Listing, Product, Symbol

def makeProductSymbolDict(listings: Dict[Symbol, Listing]) -> Dict[Product, Symbol]:
    """
    Converts the symbol -> listing dictionary into a product -> symbol dictionary
    
    Parameters:
    listings (Dict[Symbol, Listing]): The dictionary of symbols to listings
    
    Returns:
    Dict[Product, Symbol]: The dictionary of products to symbols
    """
    products = {}
    
    for symbol in listings:
        product = listings[symbol]['product'] # Wiki is incorrect: Listing is a dict, not a class
        products[product] = symbol
        
    return products

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        result = {}
        return result