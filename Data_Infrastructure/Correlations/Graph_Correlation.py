import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("order_book_data.csv", sep=";")

# get a list of all the mid prices for COCONUTS
coconut_mid_prices = []
for idx in range(0, len(df.axes[0])):
    if df['product'][idx] == 'COCONUTS':
        coconut_mid_prices.append(df['mid_price'][idx])

# get a list of all the mid prices for PINA_COLADAS
pina_colada_mid_prices = []
for idx in range(0, len(df.axes[0])):
    if df['product'][idx] == 'PINA_COLADAS':
        pina_colada_mid_prices.append(df['mid_price'][idx])

lookback = 26
correlation_over_time = []
for i in range(len(coconut_mid_prices)):
    if i < len(pina_colada_mid_prices) and i > lookback:
        correlation_over_time.append(np.corrcoef(coconut_mid_prices[i-lookback:i], pina_colada_mid_prices[i-lookback:i])[0][1])
    else:
        correlation_over_time.append(0)

plt.plot(correlation_over_time)
plt.show()

plt.savefig('Correlation_Graph_Over_Time')
