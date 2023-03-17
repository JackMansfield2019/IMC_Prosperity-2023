import matplotlib.pyplot as plt

with open('Ask_Bid.txt', 'r') as f:
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
for i in range(len(data)):
    temp = [float(x) for x in data[i].split()]
    data[i] = temp[1:]
    max_bids.append(data[i][0])
    min_asks.append(data[i][1])
    our_asks.append(data[i][2])
    our_bids.append(data[i][3])

# Plot all the found stuff
line1, = plt.plot(max_bids, label='Max Bot Bid')
line2, = plt.plot(min_asks, label='Min Bot Ask')
line3, = plt.plot(our_asks, label='Our Ask')
line4, = plt.plot(our_bids, label='Our Bid')
plt.legend(handles=[line1, line2, line3, line4])
plt.ylabel('Seashells')

# Uncomment for saving file
# plt.title(strat + ' Graph')
# plt.savefig(file_name, format='png', dpi=1200)
plt.show()
