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

Min_bound = 999999.0
Max_bound = -999999.0

Set_of_prices = {10000.0}

#histogram
vals = []
for line in lines:
    line = line.split(" ")
    if 10000.0 - float(line[1]) > Max_bound:
        Max_bound = 10000.0 - float(line[1]) 
    if 10000.0 - float(line[1]) < Min_bound:
        Min_bound = 10000.0 - float(line[1]) 
    Set_of_prices.add(float(line[1]))
    vals.append(10000.0 - float(line[1]))

print(sorted(Set_of_prices))
plt.hist(vals, bins=np.arange(Min_bound - 0.5, Max_bound+1.0,0.5))
plt.title(file_name[:-4] +" Histogram")
plt.ylabel('Frequency')
plt.xlabel('10,000 - Price')
plt.savefig(file_name[:-4] + '_Histogram.pdf')
plt.show()

