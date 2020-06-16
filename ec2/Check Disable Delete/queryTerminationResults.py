import json

count = 0

with open('output/info.json') as inp:
    d = json.load(inp)

for key,value in d.items():
    for key2,value2 in value.items():
        try:
            for key3,value3 in value2.items():
                if value3 == 'terminated':
                    # print key
                    count = count + 1
        except:
            continue
print "\n + TOTAL TERMINATED: " + str(count)