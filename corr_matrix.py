import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

df = pd.read_csv("data_test1.csv", sep=";")

#create augmented dataframe (commodities w/ their corresponding mid prices)
df_aug = pd.DataFrame(columns=["PEARLS", "BANANAS"])
for idx in range(0, len(df.axes[0]), 2):
    df_aug.loc[idx, "PEARLS"] = df["mid_price"][idx]
    df_aug.loc[idx, "BANANAS"] = df["mid_price"][idx+1]

#correlation matrix computation
corr = df_aug.astype('float64').corr()
print(corr)

#heatmap visualization
plt.figure(figsize=(10, 8))
sns.heatmap(data = corr, annot = True)
plt.show()
