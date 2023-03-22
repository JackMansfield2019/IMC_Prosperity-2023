import matplotlib.pyplot as plt
import os
import numpy as np
import math
import sys
from typing import Dict, List, Tuple

# Add the top-level directory to the path to import the datamodel package
sys.path.append('../../')
from datamodel import Order, Product, Time

# Add the parent directory to the path to import Plot_Utils
sys.path.append('../')
from Plot_Utils import parseCombinedLOB

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "<input_file> <output_directory>")
    print("<input_file> is the path to the csv file to read from")
    print("<output_directory> is the name of the directory to save the plots to")
    exit()

input_file = sys.argv[1]
sub_dir = sys.argv[2]

if not os.path.exists(input_file):
    print("Input file does not exist")
    exit(1)

if not os.path.exists(sub_dir):
    os.mkdir(sub_dir)

lob_data = parseCombinedLOB(input_file)
    
# Track ask and bid orders, map a product to a list of orders and corresponding times
ask_orders: Dict[Product, List[Tuple[Order, Time]]] = {product: [] for product in lob_data.keys()}
bid_orders: Dict[Product, List[Tuple[Order, Time]]] = {product: [] for product in lob_data.keys()}

for product in lob_data:
    for time in lob_data[product]:
        for order in lob_data[product][time][0]:
            if order.quantity > 0:
                ask_orders[product].append((order, time))
            else:
                bid_orders[product].append((order, time))

for prod in lob_data:
    vals: List[float] = []
    
    # Combine ask and bid orders
    for time in lob_data[prod]:
        largest_order_index = 0
        
        for index, order in enumerate(lob_data[prod][time][0]):
            if abs(order.quantity) > abs(lob_data[prod][time][0][largest_order_index].quantity):
                largest_order_index = index
                
        vals.append(lob_data[prod][time][0][largest_order_index].price)

    Set_of_Prices = set(vals)
    Max_bound = max(Set_of_Prices)
    Min_bound = min(Set_of_Prices)

    if prod == 'PEARLS':
        Bin_size = 0.5
    else:
        Bin_size = 1.0

    plt.hist(vals, bins=np.arange(Min_bound - Bin_size,
                                  Max_bound + 2 * Bin_size, Bin_size))

    plt.title('Price Histogram - ' + prod)
    plt.savefig(os.path.join(sub_dir, 'Hist_Prices_' + prod + '.pdf'))
    plt.show()
    plt.clf()

    size = len(vals)
    time = np.full((size,), 0)
    quote = np.full((size,), 0)

    i = 0
    for value in vals:
        time[i] = i
        quote[i] = value
        i += 1

    l = [(1.0/12.0), (1.0/96.0), (1.0/1920.0)]

    MV1 = np.zeros(shape=(size,))
    MV2 = np.zeros(shape=(size,))
    MV3 = np.zeros(shape=(size,))

    L = (1.0/12.0)
    for t in range(size):
        if t == 0:
            MV1[0] = quote[0]
            # (1-math.exp(-L))*quote[0]
        else:
            MV1[t] = math.exp(-L)*MV1[t-1]+(1-math.exp(-L))*quote[t]

    L = (1.0/96.0)
    for t in range(size):
        if t == 0:
            MV2[0] = quote[0]
            # (1-math.exp(-L))*quote[0]
        else:
            MV2[t] = math.exp(-L)*MV2[t-1]+(1-math.exp(-L))*quote[t]

    L = (1.0/1920.0)
    for t in range(size):
        if t == 0:
            MV3[0] = quote[0]
            # (1-math.exp(-L))*quote[0]
        else:
            MV3[t] = math.exp(-L)*MV3[t-1]+(1-math.exp(-L))*quote[t]

    # print(type(MV1))

    # PLOT THE LINE
    x = np.arange(0, size, 1)
    plt.plot(x, quote, label="price")
    plt.plot(x, MV1, label="1/12")
    plt.plot(x, MV2, label="1/96")
    plt.plot(x, MV3, label="1/1920")

    plt.title("Price and EMA - " + prod)
    plt.ylabel('Exponential moving average')
    plt.xlabel('Time (minutes)')
    plt.savefig(os.path.join(sub_dir, 'Price_EMA_' + prod + '.pdf'))
    plt.show()
    plt.clf()
