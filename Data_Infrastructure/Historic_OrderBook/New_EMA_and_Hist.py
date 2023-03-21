import csv
import matplotlib.pyplot as plt
import os
import numpy as np
import math


with open('Combined_HOB.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    lines = []
    for row in reader:
        lines.append(row)

fieldnames = lines.pop(0)

products = dict()
for i, line in enumerate(lines):
    if line[2] not in products:
        products[line[2]] = []
    products[line[2]].append(float(line[-2]))

vals = []
for prod in products:
    vals = products[prod]
    Set_of_Prices = set(vals)
    Max_bound = max(Set_of_Prices)
    Min_bound = min(Set_of_Prices)

    if prod == 'PEARLS':
        Bin_size = 0.5
    else:
        Bin_size = 1.0

    plt.hist(vals, bins=np.arange(Min_bound - Bin_size,
                                  Max_bound + 2 * Bin_size, Bin_size))

    plt.show()
    plt.clf()

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

    # print(type(MV1))

    # PLOT THE LINE
    x = np.arange(0, size, 1)
    plt.plot(x, quote, label="price")
    plt.plot(x, MV1, label="1/12")
    plt.plot(x, MV2, label="1/96")
    plt.plot(x, MV3, label="1/1920")

    plt.title("Exponential Moving averages vs price")
    plt.ylabel('Exponential moving average')
    plt.xlabel('Time (minutes)')

    plt.show()
    plt.clf()
