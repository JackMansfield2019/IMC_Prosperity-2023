# Graphs mid prices, correlation and PnL for COCONUTS and PINA_COLADAS
# Uses the CSV data from the end of a submission log

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List

# Read in the data
df = pd.read_csv("order_book_data.csv", sep=";")

# Get the mid proces, correlation, and PnL for COCONUTS and PINA_COLADAS
coconut_mid_prices = []
pina_colada_mid_prices = []

for idx in range(0, len(df.axes[0])):
    if df['product'][idx] == 'COCONUTS':
        coconut_mid_prices.append(df['mid_price'][idx])
    elif df['product'][idx] == 'PINA_COLADAS':
        pina_colada_mid_prices.append(df['mid_price'][idx])

lookback = 26
correlation_over_time = []
for i in range(len(coconut_mid_prices)):
    if i < len(pina_colada_mid_prices) and i > lookback:
        correlation_over_time.append(np.corrcoef(coconut_mid_prices[i-lookback:i], pina_colada_mid_prices[i-lookback:i])[0][1])
    else:
        correlation_over_time.append(0)
        
coco_pnl_data: List[float] = []
pina_pnl_data: List[float] = []

for idx in range(len(df.axes[0])):
    if df['product'][idx] == "COCONUTS":
        coco_pnl_data.append(df['profit_and_loss'][idx])
    elif df['product'][idx] == "PINA_COLADAS":
        pina_pnl_data.append(df['profit_and_loss'][idx])

# Begin plotting
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, right=0.9)

# Break into four axes
pina_price_ax = ax
coco_price_ax = ax.twinx()
corr_ax = ax.twinx()
pnl_ax = ax.twinx()

# Set the positions of the axes
pina_price_ax.yaxis.set_label_position("left")
pina_price_ax.yaxis.tick_left()
coco_price_ax.yaxis.set_label_position("left")
coco_price_ax.spines['left'].set_position(('axes', -0.07))
coco_price_ax.yaxis.tick_left()
corr_ax.yaxis.set_label_position("right")
corr_ax.yaxis.tick_right()
pnl_ax.yaxis.set_label_position("right")
pnl_ax.spines['right'].set_position(('axes', 1.07))
pnl_ax.yaxis.tick_right()

# Plot the data
pina_price_plot = pina_price_ax.plot(pina_colada_mid_prices, label='PINA MidPrice', color='blue')
coco_price_plot = coco_price_ax.plot(coconut_mid_prices, label='COCO MidPrice', color='red')
corr_plot = corr_ax.plot(correlation_over_time, label='Correlation', color='green')
coco_pnl_plot = pnl_ax.plot(coco_pnl_data, label='COCO PnL', color='orange')
pina_pnl_plot = pnl_ax.plot(pina_pnl_data, label='PINA PnL', color='yellow')

# Set the labels
ax.set_xlabel("Time")
pina_price_ax.set_ylabel("PINA Seashells")
coco_price_ax.set_ylabel("COCO Seashells")
corr_ax.set_ylabel("Correlation")
pnl_ax.set_ylabel("PnL Seashells")

# Add lines for correlation thresholds
corr_ax_lower, corr_ax_upper = corr_ax.get_ylim()

# These constants should be the same as the ones in the strategy file
UPPER_CORR_THRESHOLD = 0.5
CORR_LOOKBACK_THRESHOLD = 0.7
LOWER_CORR_THRESHOLD = 0.25

corr_ax.axhline(y=UPPER_CORR_THRESHOLD, color='red', linestyle='--')
corr_ax.axhline(y=CORR_LOOKBACK_THRESHOLD, color='blue', linestyle='--')
corr_ax.axhline(y=LOWER_CORR_THRESHOLD, color='green', linestyle='--')

# Set the legend, show the plot, and save it
fig.legend()
plt.savefig("Correlation_Mid_PnL.pdf")
plt.show()
