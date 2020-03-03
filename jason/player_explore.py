import requests
import time
from dotenv import load_dotenv
import os
from requests.exceptions import HTTPError

load_dotenv()
secret_key=os.getenv("JASON_KEY")
SET_HEADERS={'Authorization':f'Token {secret_key}'}

LAMBDA_SERVER='https://lambda-treasure-hunt.herokuapp.com/api/adv/'
OS_SERVER=''
SERVER=LAMBDA_SERVER

#Current map supplied by server
map = {}
for x in range(500):
    map[x]={"n": "?", "s": "?", "e": "?", "w": "?"}
# Create oposites list
reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e", 'x': 'x'}

# #Cooldown



#init character
# requests.header['Authorization']='Token {secret_key}'

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
# pull OS values
# curr_map=response.map
# curr_roominfo=response.roominfo
# curr_team_locations=response.teamlocations

print(curr_room,curr_coordinates,exits,cooldown)

def update_map():
    if last_data['direction']!=None:
        # print("WTTF",last_room,map[last_room][reverse_dirs[last_data['direction']]],curr_room)
        map[last_room][last_data['direction']]=curr_room
        # print("WTTF2",curr_room,map[curr_room][reverse_dirs[current_data['direction']]],last_room)
        map[curr_room][reverse_dirs[current_data['direction']]]=last_room
        print(map[curr_room], map[last_room])
    return map

#Start walk loop
# while True:
directions_list=[{"direction":"w"},{"direction":"e"},{"direction":"e"},{"direction":"w"}] 
#,{"direction":"n"},{"direction":"w"},{"direction":"e"},{"direction":"s"}
current_data=directions_list[0]
for trials in range(len(directions_list)):
    time.sleep(cooldown - ((time.time() - starttime) % cooldown))
    # print(f"Wake {time.time()-starttime}")

    #Choose next action
    current_action='move/'

    #Choose next action data
    current_data=directions_list[trials]  

    # response=requests.post(SERVER+current_move, headers=SET_HEADERS, data=current_data)
    #Next Action
    if current_action=='move/':
        # Wise Explorer
        # print("WTF",current_data['direction'],map[curr_room][current_data['direction']])
        if current_data['direction']!=None and map[curr_room][current_data['direction']] !='?':
            current_data["next_room_id"]=str(map[curr_room][current_data['direction']])
        # Move 
        try:
            print("TRYING",current_action,current_data)
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
        print("ROOM",curr_room,curr_coordinates,"EXIT",exits,"COOL",cooldown)
        print("TITLE",r['title'],"\nDESC",r['description'],"\nItems:",r['items'],"\nERR:",r['errors'],"\nMSG:",r['messages'],'\n\n')
        update_map()#map,curr_room,last_room,current_data,last_data
    else:
        print("Didn't Move")
print("MAP",map[0],map[1])
#         # Check exits
#     if reverse_dirs[last_direction] in next_directions:
#         next_directions.remove(reverse_dirs[last_direction])
#     # Continue straight if possible
#     if last_direction in next_directions and player.current_room.get_room_in_direction(last_direction).id not in visited:
#         update_records(last_direction)
#     else:
#         # Otherwise turn or reorient
#         for x in next_directions:
#             # print("ROOMVIS",map[player.current_room.id],player.current_room.get_room_in_direction(x).id)
#             if player.current_room.get_room_in_direction(x).id in visited:
#                 map[player.current_room.id][x]=player.current_room.get_room_in_direction(x).id
#             if map[player.current_room.id][x]!='?':
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