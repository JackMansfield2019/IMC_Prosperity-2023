import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

df = pd.read_csv("data_test2.csv", sep=";")

#create augmented dataframe (commodities w/ their corresponding mid prices)
df_aug = pd.DataFrame(columns=[])
for elem in df["product"]:
    if elem not in columns:
        columns.append(elem)
for idx in range(0, len(df.axes[0])):
    for product in df_aug.columns:
        column_index: int = df_aug.columns.get_loc(product)
        if product == df['product'][idx]:
            df_aug.loc[df_aug[df_aug.columns[column_index]].count(), product] = df['mid_price'][idx]

#correlation matrix computation
corr = df_aug.astype('float64').corr()
print(corr)

#heatmap visualization
plt.figure(figsize=(10, 8))
sns.heatmap(data = corr, annot = True)
plt.show()
