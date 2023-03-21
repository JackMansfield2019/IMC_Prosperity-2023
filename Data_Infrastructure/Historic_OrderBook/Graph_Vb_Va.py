import matplotlib.pyplot as plt

with open('vb_va.txt', 'r') as f:
    l = f.readlines()

data = [x.strip().split() for x in l]

# for i, line in enumerate(data):
#     if i > 7:
#         break
#     print(line)


bids = []
asks = []

for i in range(7, len(data)-4):
    if len(data[i]) < 3:
        continue
    bids.append(int(data[i][1]))
    asks.append(-int(data[i][2]))

# print(bids)
# print(asks)
diff = []
for i in range(len(bids)):
    diff.append(asks[i] - bids[i])


# line1, = plt.plot(bids, label='Quantity of Bids')
# line2, = plt.plot(asks, label='Quantity of Asks')
# line3, = plt.plot(diff, label='Difference')
# plt.legend(handles=[line1, line2])
plt.plot(diff)
plt.ylabel('# of Bananas')
plt.show()
