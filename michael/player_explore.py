import requests
import time
from dotenv import load_dotenv
import os
from graph import Graph
from stack import Stack
from requests.exceptions import HTTPError

load_dotenv()

secret_key=os.getenv("MICHAEL_KEY")
SET_HEADERS={'Authorization':f'Token {secret_key}'}


SERVER='https://lambda-treasure-hunt.herokuapp.com/api/adv/'
OS_SERVER=''


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

# Call the Lambda server and initialize
response =requests.get(SERVER+'init/', headers=SET_HEADERS )
starttime=time.time()

# pull LS values
r=response.json()
curr_room=r['room_id']
curr_coordinates=r['coordinates']
exits=r['exits']
cooldown=r['cooldown']

#Print the current room's values
print("ROOM",curr_room,curr_coordinates,"EXIT",exits,"COOL",cooldown)
print("TITLE",r['title'],"\nDESC",r['description'],"\nERR:",r['errors'],"\nMSG:",r['messages'],'\n\n')

# pull OS values
# curr_map=response.map
# curr_roominfo=response.roominfo
# curr_team_locations=response.teamlocations

print(curr_room,curr_coordinates,exits,cooldown)


## Add my graph Sprint algo, adapt it for our DFT traversal.

#Start walk loop
# while True:
directions_list=[{"direction":"s"}]

# Instantiate a new Graph. Use the dft method to start a random walk to explore the 500 rooms
g = Graph()
s = Stack()
# initialize the stack with the player's current room
s.push([curr_room])
print("s: ", s)
print(s.stack)
print(s.size())
# for trials in range(len(directions_list)):
while (s.size() > 0):
    time.sleep(cooldown - ((time.time() - starttime) % cooldown))
    # print(f"Wake {time.time()-starttime}")
    # current_action='move/'
    # current_data=directions_list[trials]  
    # response=requests.post(SERVER+current_move, headers=SET_HEADERS, data=current_data)


    #Note that 'exits' could be a problem...will I receive the new exits from the API and update them to my graph correctly?
    r = g.dft(curr_room, curr_room, exits, s, directions_list)
    print("response from the dft: ", r)
    #if all rooms explored in current_room, pop last room off the stack.
    if r[0] not in g.room_graph or '?' not in list(g.room_graph[r[0]].values()):
        s.pop()

    # try:
    #     response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
    #     print(response.status_code)
    #     response.raise_for_status()
    # except HTTPError as http_err:
    #     print(f'HTTP error occurred: {http_err}')
    # except Exception as err:
    #     print(f'Other error occurred: {err}')

    starttime=time.time()
    # r=response.json()
    curr_room=r[0]
    curr_coordinates=r[1]
    exits=r[2]
    cooldown=r[3]
    s = r[4]
    directions_list = r[5]
    print("ROOM",curr_room,curr_coordinates,"EXIT",exits,"COOL",cooldown)
    # print("TITLE",r['title'],"\nDESC",r['description'],"\nERR:",r['errors'],"\nMSG:",r['messages'],'\n\n')