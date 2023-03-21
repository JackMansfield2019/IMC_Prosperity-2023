import csv

with open('Data.txt', 'r') as f:
    lines = f.readlines()

lines = [s.strip() for s in lines]


working = False
parsed = []
for line in lines:
    if len(line) == 0:
        continue

    if not working:
        parsed.append([line])
        working = True
        continue

    # Working
    if not line[0].isdigit():
        parsed[-1].append(line)
        continue

    parsed.append([line])


trades = []
for i, line in enumerate(parsed):
    line[0] = line[0].split('00 ')
    line[0].pop(0)
    line[0] = ''.join(line[0])
    parsed[i] = ' '.join(''.join(line).split(')('))
    parsed[i] = parsed[i].replace('(', '').replace(')', '').split(',')

    for j in range(len(parsed[i])):
        if j == 0 or j == len(parsed[i]) - 1:
            continue
        if j % 3 == 0:
            parsed[i][j] = parsed[i][j].split()

    for j in range(len(parsed[i])):
        if type(parsed[i][j]) == list:
            temp = parsed[i][j]
            parsed[i][j] = temp[1]
            parsed[i].insert(j, temp[0])

    for j in range(len(parsed[i])):
        if '<<' in parsed[i][j]:
            continue
        if j == 0:
            trades.append([parsed[i][j]])
            continue
        trades[-1].append(parsed[i][j])


for i in range(len(trades) - 1):
    for j in range(len(trades[i])):
        if j % 3 == 1:
            trades[i][j] = float(trades[i][j])
        elif j % 3 == 2:
            trades[i][j] = int(trades[i][j])


trades[-1][-1] = float(trades[-1][-1].replace('Submission logs:', ''))
for i in range(len(trades[-1])):
    if i % 3 == 1:
        trades[-1][i] = float(trades[-1][i])
    elif i % 3 == 2:
        trades[-1][i] = int(trades[-1][i])


fieldnames = ['timestamp', 'buyer', 'seller',
              'symbol', 'currency', 'price', 'quantity']

# for i in range(1, 65):
#     p = 'Price '
#     q = 'quantity '
#     s = 'Trade #: '
#     s = s + str(i)
#     p = p + str(i)
#     q = q + str(i)
#     fieldnames.append(s)
#     fieldnames.append(p)
#     fieldnames.append(q)


# for trade in trades:
#     print(trade)

rows = []
temp_dict = dict()
timestamp = 100

temp_dict['timestamp'] = timestamp
temp_dict['currency'] = 'SEASHELLS'
temp_dict['buyer'] = ''
temp_dict['seller'] = ''
for x, trade in enumerate(trades):
    if x < 2:
        continue
    for i, element in enumerate(trade):
        if i % 3 == 0:
            temp_dict['symbol'] = element
        elif i % 3 == 1:
            temp_dict['price'] = element
        elif i % 3 == 2:
            # i % 3 == 2
            temp_dict['quantity'] = element
            rows.append(temp_dict.copy())

    timestamp += 100
    temp_dict['timestamp'] = timestamp

for i in range(3):
    # print(trades[i])
    print(rows[i])
    # for i, trade in enumerate(trades):
    #     if i < 2 or trade[0] == '':
    #         continue

    #     temp_dict[fieldnames[0]] = timestamp
    #     for j in range(len(trades[i])):
    #         temp_dict[fieldnames[j+1]] = trades[i][j]

    #     rows.append(temp_dict.copy())
    #     temp_dict.clear()
    #     timestamp += 100

with open("Trade_Data_Tutorial.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
