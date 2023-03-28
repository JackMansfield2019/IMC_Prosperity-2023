import csv

#Meaningless comment
with open('prices_round_1_day_-2.csv', mode='r') as csv_file:
    spamreader = csv.reader(csv_file, delimiter=' ', quotechar='|')
    rounds = []
    for row in spamreader:
        rounds.append(', '.join(row).split(';'))

fieldnames = rounds.pop(0)

for round in rounds:
    for i, thing in enumerate(round):
        if i == 2:
            continue
        if thing == '':
            continue

        round[i] = float(round[i])


adder = rounds[-1][1] + 100
with open('prices_round_1_day_-1.csv', mode='r') as csv_file:
    spamreader = csv.reader(csv_file, delimiter=' ', quotechar='|')
    line_count = 0
    for row in spamreader:
        if line_count == 0:
            line_count += 1
            continue
        temp = ', '.join(row).split(';')
        for i, thing in enumerate(temp):
            if i == 2:
                continue
            if thing == '':
                continue

            temp[i] = float(thing)
        temp[1] += adder
        rounds.append(temp)

adder = rounds[-1][1] + 100
with open('prices_round_1_day_0.csv', mode='r') as csv_file:
    spamreader = csv.reader(csv_file, delimiter=' ', quotechar='|')
    line_count = 0
    for row in spamreader:
        if line_count == 0:
            line_count += 1
            continue
        temp = ', '.join(row).split(';')
        for i, thing in enumerate(temp):
            if i == 2:
                continue
            if thing == '':
                continue

            temp[i] = float(thing)
        temp[1] += adder
        rounds.append(temp)

rows = []
temp_dict = dict()
for round in rounds:
    for i in range(len(round)):
        temp_dict[fieldnames[i]] = round[i]
    rows.append(temp_dict.copy())

with open("Combined_HOB.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print('done')
