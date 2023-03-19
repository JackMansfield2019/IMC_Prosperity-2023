# Generates the following graphs for each symbol found in the given trades file:
# 1. A histogram of the trade prices
# 2. A histogram of the trade prices, weighted by volume
# 3. An exponential moving average plot of the trade prices over time

# Adapted from dataInfrastructure/Graph_Data/EMA_and_Hist.py

import math
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# Add the parent directory to the path to import Plot_Utils
import sys
sys.path.append('../')
from Plot_Utils import normalizeTo, distributionToStr, calcDynamicMMDistribution

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
    plt.title("Bot Trades Price Histogram (By Frequency) - " + symbol)
    plt.ylabel('Frequency')
    plt.xlabel('Price')
    plt.savefig(file_path)
    plt.show()
    plt.clf()

def plotTradePriceVolumeHistogram(trades: List[Trade], symbol: Symbol, file_path: str, bin_extents: int = 4) -> None:
    """
    Plot a histogram of trade prices based on volume, show it, and save it to a pdf file
    
    trades (List[Trade]): A list of trades to plot
    symbol (Symbol): The symbol of the trades
    file_path (str): The path to save the pdf file to
    bin_extents (int):  How far to extend the bins on either side of the min and max prices
    """
    quantity_sums = {}
    prices = []
    for trade in trades:
        
        if trade.price not in quantity_sums:
            quantity_sums[trade.price] = 0
            
        quantity_sums[trade.price] += trade.quantity
        prices.extend([trade.price] * trade.quantity)
        
    total_volume = sum(quantity_sums.values())
    reserved_percent = 0.1
    
    for price in sorted(quantity_sums):
        print(price, ":", quantity_sums[price], ":", quantity_sums[price]/total_volume)
    
    bins = np.arange(min(prices) - bin_extents, max(prices) + bin_extents, 1)
    plt.hist(prices, bins=bins)
    plt.title("Bot Trades Price Histogram (By Volume) - " + symbol)
    plt.ylabel('Volume')
    plt.xlabel('Price')
    plt.savefig(file_path)
    plt.show()
    plt.clf()

def plotMMDistribution(distribution: Dict[int, float], symbol: Symbol, file_path: str,
    title: str | None = None, y_label: str = "Distribution", x_label: str = "Price Level") -> None:
    """
    Plots the distribution of a market making strategy. Saves to a file and shows the plot.
    
    Parameters:
    distribution (Dict[int, float]): The distribution to plot
    symbol (Symbol): The symbol of the distribution
    file_path (str): The path to save the pdf file to
    title (str | None): The title of the plot. If None, a default title will be used.
    y_label (str): The label for the y-axis. Defaults to "Distribution"
    x_label (str): The label for the x-axis. Defaults to "Price Level"
    """
    if title is None:
        title = "Market Making Distribution - " + symbol
    
    plt.bar(list(distribution.keys()), list(distribution.values()))
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(file_path)
    plt.show()
    plt.clf()

def plotTradePriceEMA(trades: List[Trade], symbol: Symbol, file_path: str,
    multipliers: List[int] = [12, 96, 1920]) -> None:
    """
    Plot the prices and exponential moving averages of many trades prices over time, show it, and save it to a pdf file
    
    trades (List[Trade]): A list of trades to plot
    symbol (Symbol): The symbol of the trades
    file_path (str): The path to save the pdf file to
    """
    size = len(trades)
    time_data = range(size)
    prices = [trade.price for trade in trades]
    plt.plot(time_data, prices, label="Price")
        
    for mult in multipliers:
        mult_inv = (1.0/mult)
        moving_avg_data = np.zeros(shape=(size,))
        moving_avg_data[0] = prices[0]
        for t in range(1, size):
                moving_avg_data[t] = math.exp(-mult_inv) * moving_avg_data[t-1] + (1 - math.exp(-mult_inv)) * prices[t]
        plt.plot(time_data, moving_avg_data, label="1/" + str(mult))

    plt.title("Price and EMA vs Time - " + symbol)
    plt.ylabel('Price')
    plt.xlabel('Time (minutes)')
    plt.savefig(file_path)
    plt.show()
    plt.clf()

# Bananas: Use dynamic MM vol distribution
buy_range = (-5, -1)
sell_range = (1, 5)
distribution = calcDynamicMMDistribution(trades['BANANAS'], buy_range, sell_range)
plotMMDistribution(distribution, "BANANS", sub_dir + "/Bot_MM_Distribution_BANANAS.pdf")

# Normalize distribution
sell_side = {price_level: volume for price_level, volume in distribution.items()
    if buy_range[0] <= price_level <= buy_range[1]}
buy_side = {price_level: volume for price_level, volume in distribution.items()
            if sell_range[0] <= price_level <= sell_range[1]}

sell_side = normalizeTo(sell_side, 1)
buy_side = normalizeTo(buy_side, 1)
distribution = {**sell_side, **buy_side}

# Print the distribution
print(distributionToStr(distribution))

for symbol in trades:
    plotTradePriceHistogram(trades[symbol], symbol, sub_dir + "/Bot_Trades_Hist_" + symbol + ".pdf")
    plotTradePriceVolumeHistogram(trades[symbol], symbol, sub_dir + "/Bot_Trades_Hist_Volume_" + symbol + ".pdf")
    plotTradePriceEMA(trades[symbol], symbol, sub_dir + "/Bot_Trades_Exp_Mov_Avg_" + symbol + ".pdf")
