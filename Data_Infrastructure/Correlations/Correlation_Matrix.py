import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

df = pd.read_csv("data_test2.csv", sep=";")

#create augmented dataframe (commodities w/ their corresponding mid prices)
df_aug = pd.DataFrame(columns=["PEARLS", "BANANAS"])
pearl_index = 0
banana_index = 0
for idx in range(0, len(df.axes[0])):
    if df['product'][idx] == "PEARLS":
        # add the midprice to the pearls column
        df_aug.loc[pearl_index, 'PEARLS'] = df['mid_price'][idx]
        pearl_index += 1
    else:
        # add the midprice to the bananas column
        df_aug.loc[banana_index, 'BANANAS'] = df['mid_price'][idx]
        banana_index += 1

#correlation matrix computation
corr = df_aug.astype('float64').corr()
print(corr)

#heatmap visualization
plt.figure(figsize=(10, 8))
sns.heatmap(data = corr, annot = True)
plt.show()
