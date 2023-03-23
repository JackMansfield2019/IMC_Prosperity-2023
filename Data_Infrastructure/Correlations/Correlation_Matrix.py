import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

# make sure your current directory is the Correlations folder when running, and the csv is called order_book_data.csv
df = pd.read_csv("order_book_data.csv", sep=";")


#create augmented dataframe (commodities w/ their corresponding mid prices)
df_aug = pd.DataFrame(columns=[])
for elem in df["product"]:
    if elem not in df_aug.columns:
        df_aug[elem] = None
for idx in range(0, len(df.axes[0])):
    # print progress
    if idx % 10000 == 0:
        print("Progress: " + str(idx) + "/" + str(len(df.axes[0])))
    for product in df_aug.columns:
        column_index: int = df_aug.columns.get_loc(product)
        if product == df['product'][idx]:
            df_aug.loc[df_aug[df_aug.columns[column_index]].count(), product] = df['mid_price'][idx]


print("computing correlation matrix...")
#correlation matrix computation
corr = df_aug.astype('float64').corr()
print(corr)

#heatmap visualization
plt.figure(figsize=(10, 8))
sns.heatmap(data = corr, annot = True)
plt.show()
