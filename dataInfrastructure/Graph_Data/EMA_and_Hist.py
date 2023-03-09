import math
import matplotlib.pyplot as plt
import random
import numpy as np
import csv
import os
import matplotlib as mpl


sub_dir = input("Input Subdirectory: ")
prod = input("Enter Product: ")

try:
    os.mkdir(sub_dir)
except:
    print("Path Already exists")


with open('data_test2.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    lines = []
    for row in reader:
        for i in range(len(row)):
            l = row[i].split(';')
            lines.append(l)

    csv_file.close()

fieldnames = lines[0]
rows = []
temp_dict = dict()
for i, line in enumerate(lines):
    if i == 0:
        continue
    for j in range(len(fieldnames)):
        temp_dict[fieldnames[j]] = line[j]
    rows.append(temp_dict.copy())


products = dict()
for row in rows:
    if row['timestamp'] == '0':
        products[row['product']] = []
        continue
    break

for row in rows:
    products[row['product']].append(float(row['mid_price']))


# EDIT THIS LINE FOR PRODUCT DATA (i.e. products['BANANAS'] gets BANANA data)
vals = products[prod]
Set_of_Prices = set(vals)
Max_bound = max(Set_of_Prices)
Min_bound = min(Set_of_Prices)

# If Banana Bucket size is 1, Pearl is .50

print(Max_bound, Min_bound)
# plt.hist(vals, bins=np.arange(Min_bound - 0.5, Max_bound+1.0, 0.5))
if prod == 'PEARLS':
    Bin_size = 0.5
else:
    Bin_size = 1.0

plt.hist(vals, bins=np.arange(Min_bound - Bin_size,
         Max_bound + 2 * Bin_size, Bin_size))
my_path = os.path.abspath(__file__)
my_path = my_path.replace('EMA_and_Hist.py', '')
my_path = my_path + sub_dir

my_file = 'Hist.pdf'
plt.savefig(os.path.join(my_path, my_file))
plt.show()


size = len(vals)
time = np.full((size,), 0)
quote = np.full((size,), 0)


i = 0
for value in vals:
    time[i] = i
    quote[i] = value
    i += 1

l = [(1.0/12.0), (1.0/96.0), (1.0/1920.0)]


MV1 = np.zeros(shape=(size,))
MV2 = np.zeros(shape=(size,))
MV3 = np.zeros(shape=(size,))

L = (1.0/12.0)
for t in range(size):
    if t == 0:
        MV1[0] = quote[0]
        # (1-math.exp(-L))*quote[0]
    else:
        MV1[t] = math.exp(-L)*MV1[t-1]+(1-math.exp(-L))*quote[t]

L = (1.0/96.0)
for t in range(size):
    if t == 0:
        MV2[0] = quote[0]
        # (1-math.exp(-L))*quote[0]
    else:
        MV2[t] = math.exp(-L)*MV2[t-1]+(1-math.exp(-L))*quote[t]

L = (1.0/1920.0)
for t in range(size):
    if t == 0:
        MV3[0] = quote[0]
        # (1-math.exp(-L))*quote[0]
    else:
        MV3[t] = math.exp(-L)*MV3[t-1]+(1-math.exp(-L))*quote[t]

print(type(MV1))

# PLOT THE LINE
x = np.arange(0, size, 1)
plt.plot(x, quote, label="price")
plt.plot(x, MV1, label="1/12")
plt.plot(x, MV2, label="1/96")
plt.plot(x, MV3, label="1/1920")

plt.title("Exponential Moving averages vs price")
plt.ylabel('Exponential moving average')
plt.xlabel('Time (minutes)')
plt.savefig("Exp_Mov_Avg.pdf")

my_file = 'Exp_Mov_Avg.pdf'
plt.savefig(os.path.join(my_path, my_file))
plt.show()
