with open('Ask_Bid.txt', 'r') as f:
    l = f.readlines()

# for i in range(7, 10):
#     print(l[i])

data = []
for i in range(7, len(l)):
    temp = l[i].strip()
    data.append(temp)

for i in range(0, 10):
    print(data[i])
