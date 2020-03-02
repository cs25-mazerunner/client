import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

secret_key=os.getenv("JASON_KEY")

#Current map supplied by server
map = {}
# Create oposites list
reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e", 'x': 'x'}

# #Cooldown
# starttime=time.time()
# while True:
#   print "tick"
#   time.sleep(60.0 - ((time.time() - starttime) % 60.0))

#init character
# requests.header['Authorization']='Token {secret_key}'

response =requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers={'Authorization':f'Token {secret_key}'} )
# pull LS values
r=response.json()
curr_room=r['room_id']
curr_coordinates=r['coordinates']
exits=r['exits']
cooldown=r['cooldown']

# pull OS values
# curr_map=response.map
# curr_roominfo=response.roominfo
# curr_team_locations=response.teamlocations

print(curr_room,curr_coordinates,exits,cooldown)
#Start walk loop

# while True:
    # starttime=time.time()
    # while True:
    #   print "tick"
    #   time.sleep(60.0 - ((time.time() - starttime) % 60.0))
#         # Get exits
#     next_directions=player.current_room.get_exits()
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