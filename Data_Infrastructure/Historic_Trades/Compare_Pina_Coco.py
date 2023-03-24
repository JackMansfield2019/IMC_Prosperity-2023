import matplotlib.pyplot as plt


with open('Coco_Mid_Price.log', 'r') as f:
    l = f.readlines()
    f.close()

Min_Asks = [1.875 * float(x.strip().split().pop()) for x in l]


with open('Pina_MidPrice.log', 'r') as f:
    l = f.readlines()
    f.close()

Max_Bids = [float(x.strip().split().pop())  for x in l]


line1, = plt.plot(Min_Asks, label='Min Asks')
line2, = plt.plot(Max_Bids, label='Max Bids')
plt.legend(handles=[line1, line2])
plt.show()