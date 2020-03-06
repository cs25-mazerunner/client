import requests
import time
from dotenv import load_dotenv
import os
from requests.exceptions import HTTPError
import json
import sys
sys.path.append('../')
from util import Stack, Queue
import random
import hashlib
from ls8.cpu import CPU

load_dotenv()
secret_key=os.getenv("JASON_KEY")
SET_HEADERS={'Authorization':f'Token {secret_key}'}

LAMBDA_SERVER='https://lambda-treasure-hunt.herokuapp.com/api/adv/'
OS_SERVER=''
SERVER=LAMBDA_SERVER

#Current map supplied by server
player={}
important_places={'store':1,'well':55,'fly':22,'dash':461,'trans':495}
world_map={}
# for x in range(1000):
#     world_map[x]={"n": "?", "s": "?", "e": "?", "w": "?"}
# with open("map.txt",'w') as file:
#     file.write(json.dumps(world_map))
# get current Map
with open("map.txt",'r') as file:
    map_data=file.read()
    json_map = json.loads(map_data)
for item in json_map.keys():
    payload=json_map[item]
    item=int(item)
    world_map[item]=payload
#get current Room Descriptions
rooms={}
with open("room.txt",'r') as file:
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

last_block = {
    "proof": 2005690142,
    "difficulty": 6,
    "cooldown": 1.0,
    "messages": [],
    "errors": []
}

def update_map():
    if last_data['direction']!=None:
        # print("WTTF",last_room,world_map[last_room][reverse_dirs[last_data['direction']]],curr_room)
        world_map[last_room][last_data['direction']]=curr_room
        # print("WTTF2",curr_room,world_map[curr_room][reverse_dirs[current_data['direction']]],last_room)
        world_map[curr_room][reverse_dirs[current_data['direction']]]=last_room
        print("Curr Room",world_map[curr_room],"Last Room", world_map[last_room])

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

def refine(path):
    if len(path)>1:
        # print("OLD PATH",path)
        new_path=[]
        last_dir=None
        curr_rm=curr_room
        for x in range(len(path)):
            curr_dir=path[x]
            if curr_dir not in ['warp','r']:
                nxt_rm=world_map[curr_rm][curr_dir]
                # print("REFINE",x,curr_rm,curr_dir,nxt_rm)
                if last_dir==curr_dir:
                    if new_path[-1][0]=='d':
                        #add to dash
                        old_dash=new_path[-1].split(" ")
                        # print("SPLIT DASH",old_dash)
                        temp=int(old_dash[2])
                        temp+=1
                        old_dash[2]=str(temp)
                        old_dash[3]=f'{old_dash[3][:-1]}-{nxt_rm}]'
                        old_dash=" ".join(old_dash)
                        # print("JOIN DASH",old_dash)
                        new_path[-1]=old_dash
                    else:
                        #install dash
                        # d n 3 [1-2-3]
                        new_path[-1]=f'd {curr_dir} 2 [{curr_rm}-{nxt_rm}]'
                else:
                    new_path.append(curr_dir)
                # print(x,new_path)
                last_dir=curr_dir
                curr_rm=nxt_rm
            else:
                new_path.append(curr_dir)
                last_dir=curr_dir
                if curr_dir=='r':
                    curr_rm=0
                else:
                    if curr_rm<500:
                        curr_rm+=500
                    else:
                        curr_rm-=500
    else:
        new_path=list(path)
    return new_path

def weight_roomz(roomz):
    best=(float('inf'),0) # (Total,Index)
    all=[]
    for path in range(len(roomz)):
        total=0
        for item in roomz[path]:
            # print("RMZ",item)
            if item in ['warp','r']:
                total+=7
            elif item in ["n", "s", "e", "w"]:
                total+=3.15
            elif item[0]=='d':
                if item[5]==2:
                    total+=6.3
                else:
                    total+=8.5
            else:
                print("PROBLEM")
        all.append((total,path))
        if total<best[0]:
            best=(total,path)
    print("ALL",roomz,all)
    return roomz[best[1]]

def find_direction():
    found=[]
    q=Queue()
    q.enqueue((world_map[curr_room],[]))
    while q.size()>0:
        rm=q.dequeue()
        # print("ROOM",rm)
        for d in rm[0].items():
            # print("FINDER",rm[0],d,rm[1])
            if d[1]=='?':
                # print("FOUNDIT",rm[1],d[0])
                new_path=list(rm[1])
                new_path.append(d[0])
                return new_path
            elif d[1] !='x' and d[1] not in found:
                new_path=list(rm[1])
                new_path.append(d[0])
                q.enqueue((world_map[d[1]],new_path ))
                found.append(d[1])
    return found


def find_room(target):
    roomz=[]
    found=set()
    q=Queue()    
    # print("PROBLEM",r,curr_room)
    q.enqueue((world_map[curr_room],[],curr_room))
    if curr_room<500:
        warp_room=curr_room+500
        q.enqueue((world_map[warp_room],['warp'],warp_room))
        found.add(warp_room)
        q.enqueue((world_map[0],['r'],0))
    else:
        warp_room=curr_room-500
        q.enqueue((world_map[warp_room],['warp'],warp_room))
        found.add(warp_room)
        q.enqueue((world_map[0],['r'],0))
    found.add(curr_room)
    found.add(0)
    while q.size()>0:
        rm=q.dequeue()
        # print("ROOM",rm)
        for d in rm[0].items():
            # print("FIND",rm[0],d[1],type(d[1]),target)
            if d[1]==int(target):
                # print("FOUND ROOM")
                new_path=list(rm[1])
                new_path.append(d[0])
                if 'dash' in player['abilities']:
                    # print("PRE REFINE",new_path)
                    new_path=refine(new_path)
                # print(new_path)
                # sys.exit()
                roomz.append(new_path)
                # return new_path
            elif d[1] not in ['x','?'] and d[1] not in found:
                # print(rm)
                if  len(rm[1])>0 and rm[1][-1] not in ['warp','r'] and d[0]!=reverse_dirs[rm[1][-1]]:
                    new_path=list(rm[1])
                    new_path.append(d[0])
                    # print("ADDING",world_map[d[1]],new_path)  
                    q.enqueue((world_map[d[1]],new_path,d[1]))
                    found.add(d[1])
                else:
                    new_path=list(rm[1])
                    new_path.append(d[0])
                    # print("ADDING",world_map[d[1]],new_path)
                    q.enqueue((world_map[d[1]],new_path,d[1]))
                    found.add(d[1])
        if len(rm[1])>0 and rm[1][-1]!='warp':
            warp_path=list(rm[1])
            warp_path.append('warp')
            if rm[2]<500:
                warp_room=rm[2]+500
                q.enqueue((world_map[warp_room],warp_path,warp_room))
                found.add(warp_room)
            else:
                warp_room=rm[2]-500
                q.enqueue((world_map[warp_room],warp_path,warp_room))
                found.add(warp_room)
    # print("ROOMZ",roomz)
    #weighting
    test=weight_roomz(roomz)
    fastest=roomz[0]
    return fastest
        


def valid_proof(last_proof, proof):
    """
    Validates the Proof:  Does hash(last_proof, proof) contain 6
     zeroes?  Return true if the proof is valid
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f'{last_proof}{proof}'.encode()
    # print("Guess is: ", guess)
    guess_hash = hashlib.sha256(guess).hexdigest()

    return guess_hash[:6] == "000000"

def proof_of_work(last_proof):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    print("Searching for a valid proof...")
    # block_string = json.dumps(block, sort_keys=True)
    proof = 0
    while valid_proof(last_proof, proof) is False:
        proof = random.randint(900000000, 1500000000)
        # print("PROOF",proof)
    print("Finished! Valid proof is: ", proof)
    return proof

#init character
try:
    response =requests.get(SERVER+'init/', headers=SET_HEADERS )
    response.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')
starttime=time.time()
# pull LS values
r=response.json()
# while not r.get('room_id',None):
#     time.sleep(100)
curr_room=r['room_id']
curr_coordinates=r['coordinates']
exits=r['exits']
cooldown=r['cooldown']
items=r['items']
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

#Start walk loop
cmds=[]

while True:
    factor=1
    # Action IMPUT
    if current_action not in ['auto_get','auto_sell','auto_confirm','auto_walk','auto_status','auto_mine']:
        if player['encumbrance']>player['strength']*.69:
            cmds=find_room(1)
            cmds.extend(['f 555','ex well'])
            # print(f"NEW PATH to 1",cmds)
        if len(cmds)==0:
            cmds = input("-> ").lower().split(",")
        curr_cmd = cmds.pop(0).split(" ")
        if curr_cmd[0] in ["n", "s", "e", "w"]:
            current_action='move/'
            current_data={"direction":curr_cmd[0]}
        elif curr_cmd[0] in ["fn", "fs", "fe", "fw"]:
            current_action='fly/'
            current_data={"direction":curr_cmd[0][1]}
        elif curr_cmd[0] == "d":
            # d n 3 [1-2-3]
            #{"direction":"n", "num_rooms":"5", "next_room_ids":"10,19,20,63,72"}
            if curr_cmd[2]!='2':
                current_action='dash/'
                room_list=curr_cmd[3]
                # print("ROOMLIST",room_list)
                room_list=room_list[1:-1].replace('-',',')
                # print("ROOMLIST",room_list)
                current_data={"direction":curr_cmd[1], "num_rooms":curr_cmd[2], "next_room_ids":room_list}
            else:
                current_action='move/'
                current_data={"direction":curr_cmd[1]}
                cmds.insert(0,curr_cmd[1])      
        elif curr_cmd[0] == "q":
            break
        elif curr_cmd[0] == "g":
            current_action='take/'
            current_data={"name":items[0]}
        elif curr_cmd[0] == "x":
            current_action='init/'
            current_data={}
        elif curr_cmd[0] == "i":
            current_action='status/'
            current_data={}
        elif curr_cmd[0] == "o":
            current_action='sell/'
            current_data={"name":player['inventory'][0]}
            if curr_cmd[0]=="y":
                current_data['confirm']='yes'
        elif curr_cmd[0] == "a":
            print("AUTOWALK")
            current_action='move/'
            cmds=find_direction()
            cmds.append('a')
            new_dir=cmds.pop(0)
            current_data={"direction":new_dir}
        elif curr_cmd[0] == "p":
            current_action='pray/'
            current_data={}
        elif curr_cmd[0] == "t":
            current_action='transmogrify/'
            current_data={"name":player['inventory'][int(curr_cmd[1])]}
        elif curr_cmd[0] == "f":
            current_action='stay/'
            temp=cmds
            cmds=find_room(curr_cmd[1])
            cmds.extend(temp)
            # print(cmds)
            # sys.exit()
            print(f"NEW PATH to {curr_cmd[1]}",cmds)
            # new_dir=cmds.pop(0)
            # current_data={"direction":new_dir}
        elif curr_cmd[0] == "c":
            current_action='change_name/'
            current_data={"name":curr_cmd[1]}
        elif curr_cmd[0] == "ex":
            current_action="examine/"
            current_data={"name": ' '.join(curr_cmd[1:])}
        elif curr_cmd[0] == "pr":
            current_action='get_proof/'
            current_data={}            
        elif curr_cmd[0] == "m":
            current_action='mine/'
            new_proof = proof_of_work(last_block['proof'])
            current_data={"proof":new_proof}         
        elif curr_cmd[0] == "r":
            current_action='recall/'
            current_data={}            
        elif curr_cmd[0] == "b":
            current_action='get_balance/'
            current_data={}
        elif curr_cmd[0] == "+":
            current_action='carry/'
            current_data={"name":player['inventory'][int(curr_cmd[1])]}      
        elif curr_cmd[0] == "-":
            current_action='receive/'
            current_data={}
        elif curr_cmd[0] == "wear":
            current_action='wear/'
            current_data={"name":player['inventory'][int(curr_cmd[1])]}      
        elif curr_cmd[0] == "warp":
            current_action='warp/'
            current_data={}      
        elif curr_cmd[0] == "remove":
            current_action='undress/'
            if curr_cmd[1]=='b':
                current_data={"name":player['bodywear']}         
            else:
                current_data={"name":player['footwear']}   
        else:
            print("I did not understand that command.")
            current_action=None
    elif current_action=='auto_get':
        current_action='take/'
        if 'golden snitch' in items:
            current_data={"name":"golden snitch"}
        else:
            current_data={"name":items[0]}

    elif current_action=='auto_sell':
        current_action='sell/'
        current_data={"name":player['inventory'][0]}
    elif current_action=='auto_confirm':
        current_action='sell/'
        current_data={"name":player['inventory'][0],"confirm":"yes"}
    elif current_action=='auto_status':
        current_action='status/'
        current_data={}
    elif current_action=='auto_mine':
        current_action='mine/'
        new_proof = proof_of_work(last_block['proof'])
        current_data={"proof":new_proof} 
    else:
        print("I did not understand that command.")
        current_action=None


    # response=requests.post(SERVER+current_move, headers=SET_HEADERS, data=current_data)
    #Next Action
    if current_action in ['move/','fly/','dash/']:
        # Wise Explorer
        # print("WISE",current_data['direction'],world_map[curr_room][current_data['direction']])

        if current_action!='dash/' and current_data['direction']!=None and world_map[curr_room][current_data['direction']] !='?':
            current_data["next_room_id"]=str(world_map[curr_room][current_data['direction']])
            # Fly if poss
            # print("FLY",player['abilities'],rooms[world_map[curr_room][current_data['direction']]]['terrain'])
            # if 'fly' in player['abilities'] and current_action !='dash/':
            #     if rooms[world_map[curr_room][current_data['direction']]]['terrain']!='CAVE' :
            #         current_action='fly/'
            # if current_action=='fly/' and rooms[world_map[curr_room][current_data['direction']]]['terrain']=='CAVE':
            #     current_action='move/'
        if current_action!='dash/':
            current_action='fly/'
        # Move 
        # print("COOL",cooldown,time.time(),starttime)
        cooldown*=factor
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
        try:
            # print("TRYING",current_action,current_data)
            response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        starttime=time.time()
        # print("MOVE R",r)
        last_room=curr_room
        last_action=current_action
        last_data=current_data
        r=response.json()
        curr_room=r['room_id']
        curr_coordinates=r['coordinates']
        exits=r['exits']
        cooldown=r['cooldown']
        items=r['items']
        players=r['players']
        print("ROOM",curr_room,curr_coordinates,"EXIT",exits,"COOL",cooldown)
        print("TITLE",r['title'],"\nDESC",r['description'],"\nItems:",r['items'],"\nERR:",r['errors'],"\nMSG:",r['messages'],r['players'],'\n\n')
        # update_map()#map,curr_room,last_room,current_data,last_data
        # with open("map.txt",'w') as file:
        #     file.write(json.dumps(world_map))
        with open("room.txt",'w') as file:
            file.write(json.dumps(rooms))
        #Get items automatically if they are in the room.
        # if player['gold']<1000:
            if len(items)>0:
                if 'golden snitch' in items or curr_room<500:
                    print("GET IT!")
                    current_action ='auto_get'
                # cmds=['g','x']
        if curr_room==1 and len(player['inventory'])>0:
            current_action='auto_sell'
    elif current_action=='take/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        print("TAKE R",r)
        cooldown=r['cooldown']
        player['inventory'].append(current_data['name'])
        items.pop(0)
        print("Items:",r['items'],"\nMSG:",r['messages'])
        # if player['gold']<1000:
        if len(r['items'])>0 and curr_room<500:
            print("TAKE IT!")
            current_action ='auto_get'
        else:
            cmds.insert(0,'i')
    elif current_action=='status/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        # print(f"***{player}***")
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
        ,"\nAbilities:"
        ,r['abilities']
        )                  
    elif current_action=='sell/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        print(r['messages'])
        if current_data.get('confirm',None)==None:
            current_action='auto_confirm'
        elif current_data.get('confirm',None)=='yes':
            if len(player['inventory'])>0:
                player['inventory'].pop(0)
            if len(player['inventory'])>0:
                current_action='auto_sell'
            else:
                current_action='auto_status'
    elif current_action=='pray/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        print(r['messages'],'\n',r['errors'])
    elif current_action=='warp/':
        cooldown*=factor
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        # print("WARP",r)
        curr_room=r['room_id']
        curr_coordinates=r['coordinates']
        exits=r['exits']
        cooldown=r['cooldown']
        items=r['items']
        players=r['players']
        print("Cooldown",cooldown,"Players",players,r['messages'],'\n',r['errors'])
    elif current_action=='wear/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        print(r['messages'],'\n',r['errors'])
    elif current_action=='undress/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        print(r['messages'],'\n',r['errors'])
    elif current_action=='carry/':
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
        print(r['messages'],'\n',r['errors'])
    elif current_action=='receive/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        print(r['messages'],'\n',r['errors'])
    elif current_action=='transmogrify/':
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
        print(r['messages'],'\n',r['errors'])
    elif current_action=='recall/':
        cooldown*=factor
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
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
        curr_room=r['room_id']
        curr_coordinates=r['coordinates']
        exits=r['exits']
        cooldown=r['cooldown']
        items=r['items']
        players=r['players']
        print("Cooldown",r['cooldown'],r['messages'],'\n',r['errors'])
    elif current_action=='change_name/':
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
        print(r['messages'],'\n',r['errors'])
        time.sleep(cooldown - ((time.time() - starttime) % cooldown))
        current_data["confirm"]="aye"
        try:
            # print("TRYING",current_action,current_data)
            response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
    elif current_action=='examine/':
        # make a network req
        time.sleep(cooldown - ((time.time() - starttime) % cooldown))
        try:
            # print("Trying to examine...", current_action, current_data)
            response=requests.post(SERVER+current_action, headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        # if the req is good start a timer
        starttime = time.time()
        # make the data JSON
        r = response.json()
        # grab the wait time
        cooldown = r['cooldown']
        print(r["messages"], '\n', r['errors'])
        # print(r['description'])

        # with open('well_message.txt', 'w') as f:
        #     f.write(r["description"])
        if current_data['name']=="well":
            cpu = CPU()
            cpu.load(r["description"])
            save=cpu.run()
            cpu = None
            # print("SAVE",save)
            if int(save)<500:
                cmds.extend([f'f {save}','pr','m','f 55','ex well'])
            else:
                cmds.extend([f'f {save}','f 555','ex well'])
        else:
            print(r['description'])
            
    elif current_action=="get_proof/":
        # real_proof=0
        # while True:
            time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
            try:
                response=requests.get('https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/', headers=SET_HEADERS, json=current_data )
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')
            # if the req is good start a timer
            starttime = time.time()
            # make the data JSON
            r = response.json()
            # print("ASSHOLE",r)
            last_block['proof'] = r['proof']
            last_block['difficulty'] = r['difficulty']
            last_block['cooldown'] = r['cooldown']
            print("Last block: ", last_block)
            # if real_proof==0:
            #     real_proof=r['proof']
            # elif real_proof==r['proof']:
            #     continue
            # else:
            #     break
            # grab the wait time
            cooldown = r['cooldown']
            # print(r["messages"], '\n', r['errors'])
        #     time.sleep(cooldown - ((time.time() - starttime) % cooldown))
        # current_action='auto_mine'
        
    elif current_action=='mine/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
        try:
            print("Mining...", current_action, current_data)
            response=requests.post('https://lambda-treasure-hunt.herokuapp.com/api/bc/mine/', headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        # if the req is good start a timer
        starttime = time.time()
        # make the data JSON
        r = response.json()
        print(r)
        # grab the wait time
        cooldown = r['cooldown']
        # print(r["messages"], '\n', r['errors'])
    elif current_action=='get_balance/':
        # make a network req
        time.sleep(cooldown - ((time.time() - starttime) % cooldown))
        try:
            # print("Trying", current_action, current_data)
            response=requests.get('https://lambda-treasure-hunt.herokuapp.com/api/bc/get_balance/', headers=SET_HEADERS, json=current_data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        starttime = time.time()
        r = response.json()
        cooldown = r['cooldown']
        print(r)
    elif current_action=='init/':
        time.sleep(cooldown - ((time.time() - starttime) % cooldown)) 
        try:
            response =requests.get(SERVER+'init/', headers=SET_HEADERS )
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        starttime=time.time()
        # pull LS values
        r=response.json()
        # while not r.get('room_id',None):
        #     time.sleep(100)
        curr_room=r['room_id']
        curr_coordinates=r['coordinates']
        exits=r['exits']
        cooldown=r['cooldown']
        items=r['items']
        players=r['players']
        print("ROOM",curr_room,curr_coordinates,"EXIT",exits,"COOL",cooldown)
        print("TITLE",r['title'],"\nDESC",r['description'],"\nItems:",r['items'],"\nERR:",players,"\nERR:",r['errors'],"\nMSG:",r['messages'],'\n\n')        
    elif current_action=='stay/':
        pass
    else:
        print(f"Didn't Move: {current_action}")
