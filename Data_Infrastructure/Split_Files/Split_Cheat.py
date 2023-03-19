with open('cheat_data.log', 'r') as f:
    lines = f.readlines()


# print(lines[165])

s = ''
filename = ''
filenames = []
d = dict()

for i, line in enumerate(lines):
    if line == lines[164]:
        continue

    if i < 165:
        continue

    if s == '' and filename == '':
        filename = line.strip()
        filenames.append(filename)
        continue

    if '---------------' in line:
        d[filename] = s
        s = ''
        filename = ''
        continue

    s = s + line

filenames = [s.strip() for s in filenames]
print(filenames)

# # print(d.keys())
# for fname in d:
#     print(fname)
#     # with open(fname, 'w') as f:
#     #     f.write(d[fname])
#     #     f.close()
