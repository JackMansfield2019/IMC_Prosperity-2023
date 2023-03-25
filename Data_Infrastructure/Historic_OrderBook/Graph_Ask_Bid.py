import matplotlib.pyplot as plt
import requests
import json
import matplotlib.pyplot as plt
import datetime
import os

Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhMzFlOTg5Mi02MTVlLTQ3ZjQtOGZmZS1hM2M0MTkyYjUzMmIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6ImEzMWU5ODkyLTYxNWUtNDdmNC04ZmZlLWEzYzQxOTJiNTMyYiIsIm9yaWdpbl9qdGkiOiI4OWMzZDNjNy0yMGNmLTQ3YzQtODRlOC1mNjhlYmMxNDFlMmMiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiODY3MjlhZDYtZDZlNS00ZTJkLTkyYmUtNDdmYzY0YTNkZjQ4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MTQzOTYsImV4cCI6MTY3OTc3NzY1MiwiaWF0IjoxNjc5Nzc0MDUyLCJqdGkiOiJiNGNlNWUxOC1hNGMwLTQzNmMtYmQ5MS03MTUyZDIwY2MyZDciLCJlbWFpbCI6ImphY2subWFuc2ZpZWxkQGxpdmUuY29tIn0.q65FRB3Bj05ruLSMc5Mmd9oetRWiv1lQuGfAED41KXFbHU7Zhas_m7uBb5qyEmT_Z_Q0Fju8EysYXEGJwW7Y7gUvnz0GsyuTBQJHu2QH-rzXeYpij8LjtKMlaO4eREOrrIT6NKkfZ9tLw25lPhRxH-DkmExCnqHEPaac6c64TzHUcGRtgCG7THtMUSWTC7NYKc8vKENYPL3FGLSxzrShdFxnW8qZ-VOgUZ5AHiA-57o4aGNEVeaRmWB_TG54JhjIBbykpXPVLWAsr4dWZ2uh3TeT5bxg_6K01O2o7CtRQeIG-KxKuUf0RZwYY0yJ9ULjjjw8GVhsdeWJO7Ct85iddg'
Log_file_name = '90caf4a6-807a-4ccd-b841-2877688a5dad'
headers = {
    'authorization': 'Bearer '+ Cookie_id_token,
}
Response = requests.get(
    f'https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/results/tutorial/{Log_file_name}',
    headers = headers,
)
#print(Response.text)
print(Response.json()['algo']['summary']['graphLog'][16:])

def parse_input_string(input_string,timestamp_list,price_list):
    split_input = input_string.strip().split('\n')
    for i in range(0, len(split_input), 1):
        print(split_input[i])
        parts = split_input[i].split(';')
        #timestamp_list.append(int(parts[0]))
        price_list.append(float(parts[1]))
        price_list.append(float(parts[1]))
    return timestamp_list, price_list

stringI = Response.json()['algo']['summary']['graphLog'][16:]
timestamp= []
price= []
parse_input_string(stringI,timestamp,price)

#change to filename of what you want to graph

with open('bbf16834-e07a-4407-ab80-9a135751ff7b.log', 'r') as f:
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
line6, = ax2.plot(bot_price_slopes, label='Slope', color='purple')
ax3 = ax.twinx()
line7, = ax3.plot(price, label='PnL', color='yellow')
ax2.set_ylabel('Seashells')

fig.legend(handles=[line1, line3, line4, line5, line6, line7])
print(len(bot_prices))
print(len(price))
# Uncomment for saving file
# plt.title(strat + ' Graph')
plt.savefig('Jack_Bid_ask_Graph')
plt.show()
