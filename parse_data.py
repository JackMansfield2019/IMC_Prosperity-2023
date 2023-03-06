import csv

algo_trades = []

with open('data_test2.csv', 'r') as csv_file:
    tradeTracker = {}
    print("algo trades:")
    reader = csv.reader(csv_file)

    for row in reader:
        trades = row[0]
        trades = row[0].split(';')
        if(trades[-1] == "profit_and_loss"):
            print(row[0].split(';'))
            algo_trades.append(row[0])
            continue
        PNL = float(trades[-1])
        if trades[2] in tradeTracker:
            if tradeTracker[trades[2]] != PNL:
                algo_trades.append(row[0])
                print(row[0].split(';'))
                tradeTracker[trades[2]] = PNL
        else:
            tradeTracker[trades[2]] = PNL
    csv_file.close()

with open("new_algotrades.csv", mode="w") as csvfile:
    fieldnames=algo_trades[0].split(';')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trade in range(1,len(algo_trades)):
        temp_dic = {}
        ftrade = algo_trades[trade].split(';')
        count = 0
        for field in fieldnames:
            temp_dic[field] = ftrade[count]
            count+=1
        writer.writerow(temp_dic)

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


