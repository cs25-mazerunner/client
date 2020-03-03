import requests
import time
from dotenv import load_dotenv
import os
from requests.exceptions import HTTPError
import json
import sys

load_dotenv()
secret_key=os.getenv("JASON_KEY")
SET_HEADERS={'Authorization':f'Token {secret_key}'}

LAMBDA_SERVER='https://lambda-treasure-hunt.herokuapp.com/api/adv/'
OS_SERVER=''
SERVER=LAMBDA_SERVER

#Current map supplied by server
player={}
world_map={}
important_places={'store':1,'well':55}
# for x in range(500):
#     map[x]={"n": "?", "s": "?", "e": "?", "w": "?"}
#get current Map
with open("../map.txt",'r') as file:
    map_data=file.read()
    json_map = json.loads(map_data)
for item in json_map.keys():
    payload=json_map[item]
    item=int(item)
    world_map[item]=payload
#get current Room Descriptions
rooms={}
with open("../room.txt",'r') as file:
    desc_data=file.read()
    json_map = json.loads(desc_data)
for item in json_map.keys():
    payload=json_map[item]
    item=int(item)
    rooms[item]=payload
# print(world_map)
# sys.exit()
# Create oposites list
reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e", 'x': 'x'}

def update_map():
    if last_data['direction']!=None:
        # print("WTTF",last_room,world_map[last_room][reverse_dirs[last_data['direction']]],curr_room)
        world_map[last_room][last_data['direction']]=curr_room
        # print("WTTF2",curr_room,world_map[curr_room][reverse_dirs[current_data['direction']]],last_room)
        world_map[curr_room][reverse_dirs[current_data['direction']]]=last_room
        print(world_map[curr_room], world_map[last_room])

        #check for current walls
        walls = {'n', 's', 'w', 'e'}-set(exits)
        # print("WALLS",walls)
        for x in walls:
            world_map[curr_room][x] = 'x'
        rooms[curr_room]={'room_id':curr_room,
        "title": r['title'],
        "description": r['description'],
        "coordinates": r['coordinates'],
        "elevation": r['elevation'],
        "terrain": r['terrain'],
        "items": r['items'],
        "exits": r['exits'],
        "messages": r['messages'],
        }   
    return world_map

def find_direction():
    pass

#init character
response =requests.get(SERVER+'init/', headers=SET_HEADERS )
starttime=time.time()
# pull LS values
r=response.json()
curr_room=r['room_id']
curr_coordinates=r['coordinates']
exits=r['exits']
cooldown=r['cooldown']
print("ROOM",curr_room,curr_coordinates,"EXIT",exits,"COOL",cooldown)
print("TITLE",r['title'],"\nDESC",r['description'],"\nItems:",r['items'],"\nERR:",r['errors'],"\nMSG:",r['messages'],'\n\n')
time.sleep(cooldown - ((time.time() - starttime) % cooldown))
#Pull player info
current_action='status/'
current_data={}
response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
starttime=time.time()
r=response.json()
cooldown=r['cooldown']
player=dict(r)
print(player)
# pull OS values
# curr_world_map=response.map
# curr_roominfo=response.roominfo
# curr_team_locations=response.teamlocations

print(curr_room,curr_coordinates,exits,cooldown)

#Start walk loop
# while True:
# directions_list=[{"direction":"w"},{"direction":"e"},{"direction":"e"},{"direction":"w"}] #,{"direction":"e"},{"direction":"w"}
#,{"direction":"n"},{"direction":"w"},{"direction":"e"},{"direction":"s"}
# current_data=directions_list[0]
# for trials in range(len(directions_list)):
cmds=[]
while True:
    if current_action!=None:
        time.sleep(cooldown - ((time.time() - starttime) % cooldown))
    # print(f"Wake {time.time()-starttime}")

    #Choose next action

    #Choose next action data
    # current_data=directions_list[trials]  

    # Action IMPUT
    if current_action not in ['auto_get','auto_sell','auto_confirm','auto_walk']:
        if len(cmds)==0:
            cmds = input("-> ").lower().split(",")
        curr_cmd = cmds.pop(0).split(" ")
        if curr_cmd[0] in ["n", "s", "e", "w"]:
            current_action='move/'
            current_data={"direction":curr_cmd[0]}
        elif curr_cmd[0] == "q":
            break
        elif curr_cmd[0] == "g":
            current_action='take/'
            current_data={"name":r['items'][0]}
        elif curr_cmd[0] == "i":
            current_action='status/'
            current_data={}
        elif curr_cmd[0] in ["o"]:
            current_action='sell/'
            current_data={"name":player['inventory'][0]}
            if curr_cmd[0]=="y":
                current_data['confirm']='yes'
        elif curr_cmd[0] in ["a"]:
            print("AUTOWALK")
            cmds.push('a')
            current_action='move/'
            dir=find_direction()
            current_data={"direction":dir}
        else:
            print("I did not understand that command.")
            current_action=None
    elif current_action=='auto_get':
        current_action='take/'
        current_data={"name":r['items'][0]}
    elif current_action=='auto_sell':
        current_action='sell/'
        current_data={"name":player['inventory'][0]}
    elif current_action=='auto_confirm':
        current_action='sell/'
        current_data={"name":player['inventory'][0],"confirm":"yes"}
    else:
        print("I did not understand that command.")
        current_action=None


    # response=requests.post(SERVER+current_move, headers=SET_HEADERS, data=current_data)
    #Next Action
    if current_action=='move/':
        # Wise Explorer
        # print("WTF",current_data['direction'],world_map[curr_room][current_data['direction']])
        if current_data['direction']!=None and world_map[curr_room][current_data['direction']] !='?':
            current_data["next_room_id"]=str(world_map[curr_room][current_data['direction']])
        # Move 
        try:
            # print("TRYING",current_action,current_data)
            response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

        starttime=time.time()
        last_room=curr_room
        last_action=current_action
        last_data=current_data
        r=response.json()
        curr_room=r['room_id']
        curr_coordinates=r['coordinates']
        exits=r['exits']
        cooldown=r['cooldown']
        items=r['items']
        print("ROOM",curr_room,curr_coordinates,"EXIT",exits,"COOL",cooldown)
        print("TITLE",r['title'],"\nDESC",r['description'],"\nItems:",r['items'],"\nERR:",r['errors'],"\nMSG:",r['messages'],'\n\n')
        update_map()#map,curr_room,last_room,current_data,last_data
        with open("../map.txt",'w') as file:
            file.write(json.dumps(world_map))
        with open("../room.txt",'w') as file:
            file.write(json.dumps(rooms))
        #Get items automatically if they are in the room.
        if len(items)>0:
            print("GET IT!")
            current_action ='auto_get'
        if curr_room==1:
            current_action='auto_sell'
    elif current_action=='take/':
        try:
            # print("TRYING",current_action,current_data)
            response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        starttime=time.time()
        r=response.json()
        cooldown=r['cooldown']
        player['inventory'].append(current_data['name'])
        print("Items:",r['items'],"\nMSG:",r['messages'])
        if len(items)>0:
            print("GET IT!")
            current_action ='auto_get'
    elif current_action=='status/':
        try:
            # print("TRYING",current_action,current_data)
            response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        starttime=time.time()
        r=response.json()
        cooldown=r['cooldown']
        player=dict(r)
        print("Name:"
        ,r['name']
        ,"\nEncumbrance:"
        ,r['encumbrance']
        ,"\nStrength:"
        ,r['strength']
        ,"\nSpeed:"
        ,r['speed']
        ,"\nGold:"
        ,r['gold']
        ,"\nBodywear:"
        ,r['bodywear']
        ,"\nFootwear:"
        ,r['footwear']
        ,"\nInventory:"
        ,r['inventory']
        ,"\nStatus:"
        ,r['status']
        ,"\nErrors:"
        ,r['errors']
        ,"\nMessages:"
        ,r['messages']
        )                  
    elif current_action=='sell/':
        try:
            print("TRYING",current_action,current_data)
            response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        starttime=time.time()
        r=response.json()
        cooldown=r['cooldown']
        print(r['messages'])
        print("YO",current_data)
        if current_data.get('confirm',None)==None:
            current_action='auto_confirm'
        elif current_data.get('confirm',None)=='yes':
            player['inventory'].pop(0)
            if len(player['inventory'])>0:
                current_action='auto_sell'
    # elif current_action==:
    else:
        print(f"Didn't Move: {current_action}")
# print("world_map",world_map[0],world_map[1])
#         # Check exits
#     if reverse_dirs[last_direction] in next_directions:
#         next_directions.remove(reverse_dirs[last_direction])
#     # Continue straight if possible
#     if last_direction in next_directions and player.current_room.get_room_in_direction(last_direction).id not in visited:
#         update_records(last_direction)
#     else:
#         # Otherwise turn or reorient
#         for x in next_directions:
#             # print("ROOMVIS",world_map[player.current_room.id],player.current_room.get_room_in_direction(x).id)
#             if player.current_room.get_room_in_direction(x).id in visited:
#                 world_map[player.current_room.id][x]=player.current_room.get_room_in_direction(x).id
#             if world_map[player.current_room.id][x]!='?':
#                     next_directions.remove(x)
#             # print("NXTDIR",next_directions)
#         if len(next_directions)>0:
#             last_direction=random.sample(next_directions,1)[0]
#             update_records(last_direction)
#         else:
#             # re-orient
#             gotit=find_new_room(player.current_room.id)
#             # print("GOTIT",gotit,player.current_room.id)
#             for i in gotit:
#                 update_records(i)
#                 last_direction='x'

#     break