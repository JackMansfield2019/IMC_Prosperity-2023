import math
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import csv

#There's something wrong with this code

print(os.getcwd())
path = 'Round_2'

csv_file = open(path+"/Combined.csv", "r")

lines = csv_file.readlines()
lines.pop(0)

for i in range(len(lines)):
    lines[i] = lines[i].strip().split(',')[:1] + lines[i].strip().split(',')[3:]
    lines[i][0] = int(lines[i][0])
    lines[i][-1] = int(lines[i][-1])
    lines[i][-2] = float(lines[i][-2])
    lines[i].pop(2)

trades = []
for line in lines:
    if line[1] == 'BANANAS':
        trades.append(line)

trade_dict = dict()
for trade in trades:
    if trade[0] not in trade_dict:
        trade_dict[trade[0]] = []
    trade_dict[trade[0]].append(trade[-2])

with open('Bot_Prices.log', 'r') as f:
    data = f.readlines()
    f.close()

data = [int(x.strip().split().pop()) for x in data]

timestamp = 0
for i in range(len(data)):
    data[i] = [timestamp, data[i]]
    timestamp += 100


diff = 0
N = 0
for point in data:
    if point[0] not in sorted(trade_dict.keys()):
        continue

    for trade in trade_dict[point[0]]:
        diff += trade - point[1]
        N += 1

print(diff)
print(N)

std_dev = math.sqrt((diff * diff) / N)
print(std_dev)



# line1, = plt.plot(data)
# plt.title('Bot Price Volatility graph')
# plt.legend(handles = [line1])
# plt.show()