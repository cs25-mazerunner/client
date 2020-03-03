import json


jason_map={}
with open("jasonmap.txt",'r') as file:
    map_data=file.read()
    json_map = json.loads(map_data)
for item in json_map.keys():
    payload=json_map[item]
    item=int(item)
    jason_map[item]=payload

mike_map={}
with open("mikemap.txt",'r') as file:
    desc_data=file.read()
    json_map = json.loads(desc_data)
for item in json_map.keys():
    payload=json_map[item]
    item=int(item)
    mike_map[item]=payload

newmap={}
for x in range(500):
    newmap[x]={"n": "?", "s": "?", "e": "?", "w": "?"}

for x in range(500):
    # print(jason_map[x],mike_map[x])
    for i in jason_map[x]:
        # print("WTF",i,jason_map[x].get(i,None),mike_map[x].get(i,None))
        if jason_map[x][i]==mike_map[x][i]:
            newmap[x][i]=jason_map[x][i]
        elif jason_map[x][i] in [*range(500),'x'] and mike_map[x][i] in [*range(500),'x']:
            print("shit")
        elif jason_map[x][i]=='?':
                newmap[x][i]=mike_map[x][i]
        else:
             newmap[x][i]=jason_map[x][i]
# print(newmap)
with open("newmap.txt",'w') as file:
    file.write(json.dumps(newmap))
