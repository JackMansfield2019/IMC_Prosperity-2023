# Generates the following graphs for each symbol found in the given trades file:
# 1. A histogram of the trade prices
# 2. An exponential moving average plot of the trade prices over time

# Adapted from dataInfrastructure/Graph_Data/EMA_and_Hist.py

import math
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# Add the top-level directory to the path to import the datamodel package
import sys
sys.path.append('../../')
from datamodel import Trade, Symbol

from typing import Dict, List

sub_dir = input("Input Subdirectory: ")

try:
    os.mkdir(sub_dir)
except:
    print("Path Already exists")

bot_file_name = input("Input Bot Trades File Name: ")

with open(bot_file_name, 'r') as csv_file:
    reader = csv.reader(csv_file)
    lines = [line for line in reader]
    csv_file.close()

# Read each line and put the data into a dictionary
fieldnames = lines[0]
rows = []
temp_dict = dict()
for i, line in enumerate(lines):
    if i == 0:
        continue
    for j in range(len(fieldnames)):
        temp_dict[fieldnames[j]] = line[j]
    rows.append(temp_dict.copy())

trades: Dict[Symbol, List[Trade]] = {}

# Loop through each row, and add the trade to the trades dictionary
for row in rows:
    timestamp = int(row['Timestamp'])
    
    # Loop over each trade in the row
    for trade_num in range(1, 65):
        symbol = row['Trade #: ' + str(trade_num)]
        price = row['Price ' + str(trade_num)]
        quantity = row['quantity ' + str(trade_num)]
        
        # Skip this trade if it is empty
        if symbol is None or price is None or quantity is None or symbol == '' or price == '' or quantity == '':
            continue
        
        if symbol not in trades:
            trades[symbol] = []
        
        # Create a new trade and add it to the trades dictionary
        new_trade = Trade(symbol, int(float(price)), int(quantity), timestamp=timestamp)
        trades[symbol].append(new_trade)

def plotTradePriceHistogram(trades: List[Trade], symbol: Symbol, file_path: str, bin_extents: int = 4) -> None:
    """
    Plot a histogram of trade prices, show it, and save it to a pdf file
    
    trades (List[Trade]): A list of trades to plot
    symbol (Symbol): The symbol of the trades
    file_path (str): The path to save the pdf file to
    bin_extents (int):  How far to extend the bins on either side of the min and max prices
    """
    prices = [trade.price for trade in trades]
    bins = np.arange(min(prices) - bin_extents, max(prices) + bin_extents, 1)
    plt.hist(prices, bins=bins)
    plt.title("Bot Trades Price Histogram - " + symbol)
    plt.ylabel('Frequency')
    plt.xlabel('Price')
    plt.savefig(file_path)
    plt.show()
    plt.clf()

for symbol in trades:
    plotTradePriceHistogram(trades[symbol], symbol, sub_dir + "/Bot_Trades_Hist_" + symbol + ".pdf")
