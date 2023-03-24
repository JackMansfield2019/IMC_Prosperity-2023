# Generates the following graphs for each symbol found in the given trades file:
# 1. A histogram of the trade prices
# 2. A histogram of the trade prices, weighted by volume
# 3. An exponential moving average plot of the trade prices over time

# Adapted from dataInfrastructure/Graph_Data/EMA_and_Hist.py

from typing import Dict, List
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Add the parent directory to the path to import Plot_Utils
sys.path.append('../')
from Plot_Utils import normalizeTo, distributionToStr, calcDynamicMMDistribution, parseCombinedLOB, parseCombinedTrades

# Add the top-level directory to the path to import the datamodel package
sys.path.append('../../')
from datamodel import Order, Product, Time, Symbol, Trade

if len(sys.argv) != 4:
    print("Usage:", sys.argv[0], "<trades_input_file> <lob_input_file> <output_directory>")
    print("<trades_input_file> is the path to the csv file of the trades")
    print("<lob_input_file> is the path to the csv file of the limit order book")
    print("<output_directory> is the name of the directory to save the plots to")
    exit()

trades_input_file = sys.argv[1]
lob_input_file = sys.argv[2]
sub_dir = sys.argv[3]

if not os.path.exists(trades_input_file):
    print("Trades input file does not exist")
    exit(1)

if not os.path.exists(lob_input_file):
    print("LOB input file does not exist")
    exit(1)

if not os.path.exists(sub_dir):
    os.mkdir(sub_dir)

trades = parseCombinedTrades(trades_input_file)
lob_data = parseCombinedLOB(lob_input_file)

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
        print(price, ":", quantity_sums[price],
              ":", quantity_sums[price]/total_volume)

    bins = np.arange(min(prices) - bin_extents, max(prices) + bin_extents, 1)
    plt.hist(prices, bins=bins)
    plt.title("Bot Trades Price Histogram (By Volume) - " + symbol)
    plt.ylabel('Volume')
    plt.xlabel('Price')
    plt.savefig(file_path)
    plt.show()
    plt.clf()


def plotMMDistribution(distribution: Dict[int, float], symbol: Symbol, file_path: str,
                       title: str or None = None, y_label: str = "Distribution", x_label: str = "Price Level") -> None:
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
            moving_avg_data[t] = math.exp(-mult_inv) * moving_avg_data[t-1] + \
                (1 - math.exp(-mult_inv)) * prices[t]
        plt.plot(time_data, moving_avg_data, label="1/" + str(mult))

    plt.title("Price and EMA vs Time - " + symbol)
    plt.ylabel('Price')
    plt.xlabel('Time (minutes)')
    plt.savefig(file_path)
    plt.show()
    plt.clf()


PROD = "COCONUTS"

#mid_prices = [lob_data[PROD][time][1] for time in trades[PROD]]

orders: Dict[Time, List[Order]] = {}

for time in lob_data[PROD]:
    orders[time] = []
    
    for order in lob_data[PROD][time][0]:
        orders[time].append(order)
    
# Bananas: Use dynamic MM vol distribution
buy_range = (-7, -1)
sell_range = (1, 7)
distribution = calcDynamicMMDistribution(trades[PROD], orders, buy_range, sell_range)

plotMMDistribution(distribution, PROD, sub_dir +
                   "/Bot_MM_Distribution_" + PROD + ".pdf")

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
exit(0)

for symbol in trades:
    plotTradePriceHistogram(
        trades[symbol], symbol, sub_dir + "/Bot_Trades_Hist_" + symbol + ".pdf")
    plotTradePriceVolumeHistogram(
        trades[symbol], symbol, sub_dir + "/Bot_Trades_Hist_Volume_" + symbol + ".pdf")
    plotTradePriceEMA(trades[symbol], symbol, sub_dir +
                      "/Bot_Trades_Exp_Mov_Avg_" + symbol + ".pdf")
