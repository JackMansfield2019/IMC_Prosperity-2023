import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

# make sure your current directory is the Correlations folder when running, and the csv is called order_book_data.csv
df = pd.read_csv("order_book_data.csv", sep=";")

USE_PRODUCTS = ["DIP", "BAGUETTE", "UKULELE", "PICNIC_BASKET"]

#create augmented dataframe (commodities w/ their corresponding mid prices)
df_aug = pd.DataFrame(columns=[])
for elem in df["product"]:
    if elem not in df_aug.columns and elem in USE_PRODUCTS:
        df_aug[elem] = None
for idx in range(0, len(df.axes[0])):
    # print progress
    if idx % 10000 == 0:
        print("Progress: " + str(idx) + "/" + str(len(df.axes[0])))
    
    if df['product'][idx] not in USE_PRODUCTS:
        continue
    
    column_index = df_aug.columns.get_loc(df['product'][idx])
    df_aug.loc[df_aug[df_aug.columns[column_index]].count(), df['product'][idx]] = df['mid_price'][idx]


# Add an index for the calculation of the PICNIC index
df_aug.insert(0, "PICNIC_INDEX", None)

# Loop over rows in df_aug
for idx in range(0, len(df_aug.axes[0])):
    # print progress
    if idx % 10000 == 0:
        print("Index Adding Progress: " + str(idx) + "/" + str(len(df.axes[0])))
    
    # Set the entry to be the sum of the products
    df_aug.loc[idx, "PICNIC_INDEX"] = df_aug.loc[idx, "DIP"] * 4 + df_aug.loc[idx, "BAGUETTE"] * 2 + df_aug.loc[idx, "UKULELE"]

print("computing correlation matrix...")
#correlation matrix computation
corr = df_aug.astype('float64').corr()
print(corr)

#heatmap visualization
plt.figure(figsize=(10, 8))
sns.heatmap(data = corr, annot = True)
plt.show()
