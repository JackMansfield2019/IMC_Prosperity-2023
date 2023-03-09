import random
import numpy as np
#import Tkinter
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import math

'''
open ibm data
1st colum = time
2nd column = quote: (bid + ask)/2
'''
'''
plot the original 
'''
file_name = 'PEARLS.txt'
with open(file_name, 'r') as f:
    lines = f.readlines()


size = len(lines)
time = np.full((size,), 0)
quote = np.full((size,), 0)


i = 0
for line in lines:
    arr = line.split(" ")
    time[i] =float(arr[0])
    quote[i] = float(arr[1].replace("\n", ""))
    i+=1

l = [(1.0/12.0),(1.0/96.0),(1.0/1920.0)]


MV1 = np.zeros(shape = (size,))
MV2 = np.zeros(shape = (size,))
MV3 = np.zeros(shape = (size,))

L = (1.0/12.0)
for t in range(size):
    if t == 0:
        MV1[0] = quote[0]
        #(1-math.exp(-L))*quote[0]
    else:
        MV1[t] = math.exp(-L)*MV1[t-1]+(1-math.exp(-L))*quote[t]

L = (1.0/96.0) 
for t in range(size):
    if t == 0:
        MV2[0] = quote[0]
        #(1-math.exp(-L))*quote[0]
    else:
        MV2[t] = math.exp(-L)*MV2[t-1]+(1-math.exp(-L))*quote[t]

L = (1.0/1920.0)
for t in range(size):
    if t == 0:
        MV3[0] = quote[0]
        #(1-math.exp(-L))*quote[0]
    else:
        MV3[t] = math.exp(-L)*MV3[t-1]+(1-math.exp(-L))*quote[t]

print(type(MV1))

#PLOT THE LINE
x = np.arange(0, size,1)
plt.plot( x, quote, label = "price")
plt.plot( x, MV1, label = "1/12")
plt.plot( x, MV2, label = "1/96")
plt.plot( x, MV3, label = "1/1920")

plt.title("Exponential Moving averages vs price")
plt.ylabel('Exponential moving average')
plt.xlabel('Time (minutes)')
plt.savefig(file_name[:-4] + '_Exp_Mov_Avg.pdf')
plt.show()



