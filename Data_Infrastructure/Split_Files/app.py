import os
import json
from json import JSONEncoder
from datamodel import *
from trader import Trader
import jsonpickle

trader = Trader()

        
def lambda_handler(event, context):
    trading_state = event.get("TRADING_STATE")
    trading_state = jsonpickle.decode(trading_state)
    updated_order_depths: Dict[Symbol, OrderDepth] = {}
    for product in trading_state.order_depths:
        buy_orders: Dict[int, int] = {}
        sell_orders: Dict[int, int] = {}
        originalOrderDepth:  OrderDepth = trading_state.order_depths[product]
        targetOrderDepth = OrderDepth()
        for price in originalOrderDepth.buy_orders:
            buy_orders[int(price)] = originalOrderDepth.buy_orders[price]
        for price in originalOrderDepth.sell_orders:
            sell_orders[int(price)] = originalOrderDepth.sell_orders[price]
            
        targetOrderDepth.buy_orders = buy_orders
        targetOrderDepth.sell_orders = sell_orders
        updated_order_depths[product] = targetOrderDepth
        
    trading_state.order_depths = updated_order_depths     
      
    orders = trader.run(trading_state)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "Orders": orders
        }, cls=ProsperityEncoder)
    }
