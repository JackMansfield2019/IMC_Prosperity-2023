import csv

with open('data_test2.csv', 'r') as csv_file:
    tradeTracker = {}
    print("algo trades:")
    reader = csv.reader(csv_file)

    for row in reader:
        trades = row[0]
        trades = row[0].split(';')
        if(trades[-1] == "profit_and_loss"):
            
            continue
        PNL = float(trades[-1])
        if trades[2] in tradeTracker:
            if tradeTracker[trades[2]] != PNL:
                print(row[0].split(';'))
                tradeTracker[trades[2]] = PNL
        else:
            tradeTracker[trades[2]] = PNL
    

    
    csv_file.close()
