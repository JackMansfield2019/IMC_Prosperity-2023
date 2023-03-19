import os
import json
from json import JSONEncoder
from datamodel import *
from trader import Trader
import jsonpickle
from unittest.signals import _results

trader = Trader()

event = ${EVENT}

trading_state = jsonpickle.decode(event.get("TRADING_STATE"))

_result_ = {
        "body": json.dumps({
            "Orders": trader.run(trading_state)
        }, cls=ProsperityEncoder)
    }

print("RESULT_JSON=")
print(_result_)
