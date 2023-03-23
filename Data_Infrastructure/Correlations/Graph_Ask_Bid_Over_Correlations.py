import matplotlib.pyplot as plt
import requests
import json
import matplotlib.pyplot as plt
import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("order_book_data.csv", sep=";")

# get a list of all the mid prices for COCONUTS
coconut_mid_prices = []
for idx in range(0, len(df.axes[0])):
    if df['product'][idx] == 'COCONUTS':
        coconut_mid_prices.append(df['mid_price'][idx])

# get a list of all the mid prices for PINA_COLADAS
pina_colada_mid_prices = []
for idx in range(0, len(df.axes[0])):
    if df['product'][idx] == 'PINA_COLADAS':
        pina_colada_mid_prices.append(df['mid_price'][idx])

lookback = 26
correlation_over_time = []
for i in range(len(coconut_mid_prices)):
    if i < len(pina_colada_mid_prices) and i > lookback:
        correlation_over_time.append(np.corrcoef(coconut_mid_prices[i-lookback:i], pina_colada_mid_prices[i-lookback:i])[0][1])
    else:
        correlation_over_time.append(0)

plt.plot(correlation_over_time)
plt.show()

plt.savefig('Correlation_Graph_Over_Time')


#change to filename of what you want to graph

with open('tmp.log', 'r') as f:
    l = f.readlines()

# Uncomment if you want to get strat and save to file
# *Note: Graph is very low quality in pdf and png form
# strat = input("Enter Strategy Name: ")
# file_name = strat + '_Graph.png'

# Strip lines get rid of jargon at beginning and end of file
data = []
for i in range(7, len(l)-3):
    temp = l[i].strip()
    data.append(temp)

# Get all the stuff to print
max_bids = []
min_asks = []
our_asks = []
our_bids = []
bot_prices = []
bot_price_slopes = []

for i in range(len(data)):
    temp = [float(x) for x in data[i].split()]
    data[i] = temp[1:]
    max_bids.append(data[i][0])
    min_asks.append(data[i][1])
    our_asks.append(data[i][2])
    our_bids.append(data[i][3])
    bot_prices.append(data[i][4])
    
    BOT_SLOPE_LOOKBACK = 7

    if i < BOT_SLOPE_LOOKBACK:
        bot_price_slopes.append(0)
    else:
        bot_price_slopes.append(data[i][4] - data[i-BOT_SLOPE_LOOKBACK][4])

# Plot all the found stuff
Mid_Prices = []
for i in range(len(max_bids)):
    Mid_Prices.append((max_bids[i] + min_asks[i])/2.0)

fig, ax = plt.subplots()

line1, = ax.plot(Mid_Prices, label='MidPrice')
# line2, = plt.plot(min_asks, label='Min Bot Ask')
line3, = ax.plot(our_asks, label='Our Ask')
line4, = ax.plot(our_bids, label='Our Bid')
line5, = ax.plot(bot_prices, label='Bot Price')
ax.set_ylabel('Seashells')

ax2 = ax.twinx()
line6, = ax2.plot(correlation_over_time, label='PnL')
ax2.set_ylabel('Correlation')

fig.legend(handles=[line1, line3, line4, line5, line6])
print(len(bot_prices))
print(len(correlation_over_time))
# Uncomment for saving file
# plt.title(strat + ' Graph')
plt.savefig('Jack_Bid_ask_Graph')
plt.show()
