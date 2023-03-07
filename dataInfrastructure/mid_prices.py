import csv

mid_prices = []

threshold = 199900*0.75

#dictionary to keep track of products
with open('data_test2.csv', 'r') as csv_file:
    tradeTracker = {}
    print("Mid prices:")
    reader = csv.reader(csv_file)


    for row in reader:
        
        trades = row[0]
        trades = row[0].split(';')
        if(trades[-1] == "profit_and_loss"):
            continue

        if(float(trades[1]) > threshold):
            break
        
        if trades[3] == '':
            trades[3] = 0
        if trades[5] == '':
            trades[5] = 0
        if trades[7] == '':
            trades[7] = 0
        if trades[9] == '':
            trades[9] = 0
        if trades[11] == '':
            trades[11] = 0
        if trades[13] == '':
            trades[13] = 0
        

        bid_price = max(float(trades[3]), float(trades[5]), float(trades[7]))
        ask_price = min(float(trades[9]), float(trades[11]), float(trades[13]))
        mid_price = float((bid_price+ask_price)/2)

        mid_prices.append([trades[1], trades[2], mid_price])
    csv_file.close()

#3,5,7 are all bid prices (can be blank)
#9,11,13 are all ask prices (can be balnk)
#goes until 199900*0.75 this and keep going until you get past that value timestamp
with open("new_midprices.csv", mode="w") as csvfile:
    print(mid_prices)
    fieldnames= ["timestamp", "product", "midprice"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trade in mid_prices:
        print(trade)
        temp_dic = {}
        count = 0
        for field in fieldnames:
            temp_dic[field] = trade[count]
            count+=1
        writer.writerow(temp_dic)

"""
with open("all_algotrades.csv", mode="a", newline='') as csvfile:
    fieldnames=algo_trades[0].split(';')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for trade in range(1,len(algo_trades)):
        temp_dic = {}
        ftrade = algo_trades[trade].split(';')
        count = 0
        for field in fieldnames:
            temp_dic[field] = ftrade[count]
            count+=1
        writer.writerow(temp_dic) 
"""