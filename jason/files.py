import json

important_places={'store':1,'well':55,'fly':22,'dash':461}
world_map={}
with open("map.txt",'r') as file:
    map_data=file.read()
    json_map = json.loads(map_data)
for item in json_map.keys():
    payload=json_map[item]
    item=int(item)
    world_map[item]=payload

rooms={}
with open("room.txt",'r') as file:
    desc_data=file.read()
    json_map = json.loads(desc_data)
for item in json_map.keys():
    payload=json_map[item]
    item=int(item)
    rooms[item]=payload

count=0
for x in rooms:
    count+=1
    if rooms[x]['title'] not in ['A misty room','A Dark Cave','Mt. Holloway']:
        print(f"{x} {rooms[x]['title']} - {rooms[x]['description']}")
print("COUNT",count)

# count=0
# for x in world_map:
#     for d in world_map[x].values():
#         if d=='?':
#             count+=1
# print(count)

# missing=''
# count=0
# for x in range(500):
#     if not rooms.get(x,None):
#         missing+=f'f {x},'
#         count+=1
# print(count,missing)

# for x in rooms:
#     count+=1
#     if rooms[x]['items']!=[]:
#         print(f"{x} {rooms[x]['title']} - {rooms[x]['items']}")
# print(count)