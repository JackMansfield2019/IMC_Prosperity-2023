import math
import matplotlib.pyplot as plt
import random
import numpy as np
import csv
import os
import matplotlib as mpl

# Add the top-level directory to the path to import the datamodel package
import sys
sys.path.append('../../')
from datamodel import Order, Product, Time

from typing import Dict, List, Tuple

sub_dir = input("Input Subdirectory: ")

try:
    os.mkdir(sub_dir)
except:
    print("Path Already exists")


with open('Basic_Log.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    lines = []
    for row in reader:
        for i in range(len(row)):
            l = row[i].split(';')
            lines.append(l)

    csv_file.close()

fieldnames = lines[0]
rows = []
temp_dict = dict()
for i, line in enumerate(lines):
    if i == 0:
        continue
    for j in range(len(fieldnames)):
        temp_dict[fieldnames[j]] = line[j]
    rows.append(temp_dict.copy())


products = dict()
for row in rows:
    if row['timestamp'] == '0':
        products[row['product']] = []
        continue
    break

# Track ask and bid orders, map a product to a list of orders and corresponding times
ask_orders: Dict[Product, List[Tuple[Order, Time]]] = {product: [] for product in products}
bid_orders: Dict[Product, List[Tuple[Order, Time]]] = {product: [] for product in products}

for row in rows:
    products[row['product']].append(float(row['mid_price']))
    timestamp: Time = int(row['timestamp'])
    product = row['product']
    
    # Parse all the trades and add them to the lists of orders
    for trade_num in range(1, 4):
        bid_price = row['bid_price_' + str(trade_num)]
        bid_vol = row['bid_volume_' + str(trade_num)]
        
        if not (bid_price is None or bid_vol is None or bid_price == '' or bid_vol == ''):
            bid_orders[product].append((Order(product, int(float(bid_price)), int(bid_vol)), timestamp))
        
        ask_price = row['ask_price_' + str(trade_num)]
        ask_vol = row['ask_volume_' + str(trade_num)]
        
        if not(ask_price is None or ask_vol is None or ask_price == '' or ask_vol == ''):
            ask_orders[product].append((Order(product, int(float(ask_price)), int(ask_vol)), timestamp))

# EDIT THIS LINE FOR PRODUCT DATA (i.e. products['BANANAS'] gets BANANA data)
my_path = os.path.abspath(__file__)
my_path = my_path.replace('EMA_and_Hist.py', '')
my_path = my_path + sub_dir

for prod in products:
    vals = products[prod]
    Set_of_Prices = set(vals)
    Max_bound = max(Set_of_Prices)
    Min_bound = min(Set_of_Prices)

    # If Banana Bucket size is 1, Pearl is .50
    if prod == 'PEARLS':
        Bin_size = 0.5
    else:
        Bin_size = 1.0

    plt.hist(vals, bins=np.arange(Min_bound - Bin_size,
                                  Max_bound + 2 * Bin_size, Bin_size))

    my_file = 'Hist' + prod + '.pdf'
    plt.savefig(os.path.join(my_path, my_file))
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

    print(type(MV1))

    # PLOT THE LINE
    x = np.arange(0, size, 1)
    plt.plot(x, quote, label="price")
    plt.plot(x, MV1, label="1/12")
    plt.plot(x, MV2, label="1/96")
    plt.plot(x, MV3, label="1/1920")

    plt.title("Exponential Moving averages vs price")
    plt.ylabel('Exponential moving average')
    plt.xlabel('Time (minutes)')
    plt.savefig("Exp_Mov_Avg.pdf")

    my_file = 'Exp_Mov_Avg' + prod + '.pdf'
    plt.savefig(os.path.join(my_path, my_file))
    plt.show()
    plt.clf()

    # Create a plot of bid/ask spread
    bid_plot_data = np.zeros(shape=(size,))
    ask_plot_data = np.zeros(shape=(size,))
    spread_plot_data = np.zeros(shape=(size,))
    
    # Timestamps are incremented by 100 each time, so we divide by 100 to get the index
    # Take the max bid price and min ask price for each time interval
    for bid_order, timestamp in bid_orders[prod]:
        bid_plot_data[int(timestamp / 100)] = max(bid_plot_data[int(timestamp / 100)], bid_order.price)
        
    for ask_order, timestamp in ask_orders[prod]:
        if ask_plot_data[int(timestamp / 100)] == 0:
            ask_plot_data[int(timestamp / 100)] = ask_order.price
        else:
            ask_plot_data[int(timestamp / 100)] = min(ask_plot_data[int(timestamp / 100)], ask_order.price)
    
    # Calculate the spread
    for i in range(size):
        spread_plot_data[i] = ask_plot_data[i] - bid_plot_data[i]
    
    plt.plot(x, spread_plot_data, label="Spread")
    plt.title("Bid/Ask Spread vs Time - " + prod)
    plt.ylabel('Price')
    plt.xlabel('Time (minutes)')
    plt.savefig(os.path.join(my_path, "Bid_Ask_Spread_" + prod + ".pdf"))
    plt.show()
    plt.clf()
