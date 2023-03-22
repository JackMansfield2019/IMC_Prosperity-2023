import matplotlib.pyplot as plt

#change to filename of what you want to graph

with open('MM_Slope5_Off5_Thresh75.log', 'r') as f:
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
line6, = ax2.plot(bot_price_slopes, label='Bot Price Slope')
ax2.set_ylabel('Seashells')

fig.legend(handles=[line1, line3, line4, line5, line6])

# Uncomment for saving file
# plt.title(strat + ' Graph')
plt.savefig('Jack_Bid_ask_Graph')
plt.show()
