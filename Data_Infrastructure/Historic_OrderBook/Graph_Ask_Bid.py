import matplotlib.pyplot as plt
import requests
import json
import matplotlib.pyplot as plt
import datetime
import os

Cookie_id_token = 'eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI5ZDg2ZmJmZC00MGViLTRjY2UtYTExNS03ODYyYWFkMDVhN2MiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6IjlkODZmYmZkLTQwZWItNGNjZS1hMTE1LTc4NjJhYWQwNWE3YyIsIm9yaWdpbl9qdGkiOiJkMDFjODNjNy0zYTZiLTQyZGItOTFmZC1hOThkYTc4NDAxNWIiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiZTQyMmZmMGUtMzFlNy00YjlkLTg5ZWYtNWVjZmZjZTdmMjhkIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2Nzc2MjkyODMsImV4cCI6MTY3OTk0OTM3NSwiaWF0IjoxNjc5OTQ1Nzc1LCJqdGkiOiI3NWZhNGQ3Ny01OWM2LTQwY2UtODRjOC1lNzkxZTNlNWUxOWUiLCJlbWFpbCI6InJ5YW5jcml2QGdtYWlsLmNvbSJ9.Gz4oAiquEvDy3m8rpvQ3nQ8VI8WQXpO-SS7uSNEjAT0H3cgfYiWEtDCVtglvz8YanNqqv0QWgRg52vWeOd3R1-GfyBGXuVdteXHIWGEHiPivMnVnJhVff2GOwYpcKr35b0kGh1A12sn86zoxDpNb0FGVeqH0MHx0BH0iUWyv35Ksb0TYUUDkdqTRlD-XGOWcv6Roq1ZG45oB2ueaJ6JGVOK_5UaBa2qzOF_mSKcR_FD7pQNsOjHCDyhlWul35ZtgzKtzJKnfM_kc_7nfHgMIn1hldxQaJ08y2kpIMWS0VGcpRV2Rv3pD68-m73WIujW3CANh2a-doFSS06PTEIE96w'
Log_file_name = '756a1e30-4fe8-48a0-8b1f-d4988cf7e8ae'
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

with open('756a1e30-4fe8-48a0-8b1f-d4988cf7e8ae.log', 'r') as f:
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
our_position = []


for i in range(len(data)):
    temp = [float(x) for x in data[i].split()]
    data[i] = temp[1:]
    max_bids.append(data[i][0])
    min_asks.append(data[i][1])
    our_asks.append(data[i][2])
    our_bids.append(data[i][3])
    bot_prices.append(data[i][4])
    our_position.append(data[i][5])
    
    # BOT_SLOPE_LOOKBACK = 7

    # if i < BOT_SLOPE_LOOKBACK:
    #     bot_price_slopes.append(0)
    # else:
    #     bot_price_slopes.append(data[i][4] - data[i-BOT_SLOPE_LOOKBACK][4])

# Plot all the found stuff
Mid_Prices = []
for i in range(len(max_bids)):
    Mid_Prices.append((max_bids[i] + min_asks[i])/2.0)

fig, ax = plt.subplots()

line1, = ax.plot(max_bids, label='Max Bot Bid')
line2, = plt.plot(min_asks, label='Min Bot Ask')
line3, = ax.plot(Mid_Prices, label='Mid Prices')
# line3, = ax.plot(our_asks, label='Our Ask')
# line4, = ax.plot(our_bids, label='Our Bid')
# line5, = ax.plot(bot_prices, label='Bot Price')
ax.set_ylabel('Seashells')

ax2 = ax.twinx()
line6, = ax2.plot(our_position, label='Position', color='purple')
ax3 = ax.twinx()
line7, = ax3.plot(price, label='PnL', color='yellow')
ax2.set_ylabel('Seashells')

fig.legend(handles=[line1, line2, line3, line6, line7])
print(len(bot_prices))
print(len(price))
# Uncomment for saving file
# plt.title(strat + ' Graph')
plt.savefig('Jack_Bid_ask_Graph')
plt.show()
