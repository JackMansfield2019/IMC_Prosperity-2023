import csv

with open('trades_round_1_day_-2.csv', mode='r') as csv_file:
    spamreader = csv.reader(csv_file, delimiter=' ', quotechar='|')
    trades = []
    for row in spamreader:
        trades.append(', '.join(row).split(';'))


fieldnames = trades.pop(0)
for i, line in enumerate(trades):
    trades[i][0] = int(line[0])
    trades[i][-2] = float(line[-2])
    trades[i][-1] = int(line[-1])


adder = trades[-1][0] + 100
with open('trades_round_1_day_-1.csv', mode='r') as csv_file:
    spamreader = csv.reader(csv_file, delimiter=' ', quotechar='|')
    line_count = 0
    for row in spamreader:
        if line_count == 0:
            line_count += 1
            continue
        temp = ', '.join(row).split(';')
        temp[0] = int(temp[0]) + adder
        temp[-2] = float(temp[-2])
        temp[-1] = int(temp[-1])
        trades.append(temp)

adder = trades[-1][0]
with open('trades_round_1_day_0.csv', mode='r') as csv_file:
    spamreader = csv.reader(csv_file, delimiter=' ', quotechar='|')
    line_count = 0
    for row in spamreader:
        if line_count == 0:
            line_count += 1
            continue
        temp = ', '.join(row).split(';')
        temp[0] = int(temp[0]) + adder
        temp[-2] = float(temp[-2])
        temp[-1] = int(temp[-1])
        trades.append(temp)

rows = []
temp_dict = dict()
for trade in trades:
    for i in range(len(trade)):
        temp_dict[fieldnames[i]] = trade[i]
    rows.append(temp_dict.copy())

with open("Combined.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
