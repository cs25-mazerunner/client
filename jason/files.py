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

