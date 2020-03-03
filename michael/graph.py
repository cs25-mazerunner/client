from stack import Stack
import requests
import os
from requests.exceptions import HTTPError

secret_key=os.getenv("MICHAEL_KEY")
SET_HEADERS={'Authorization':f'Token {secret_key}'}

SERVER='https://lambda-treasure-hunt.herokuapp.com/api/adv/'


class Graph:

    """Represent a graph as a dictionary of vertices mapping labels to edges."""
    def __init__(self):
        self.room_graph = {}

    def add_room(self, room_id):
        """
        Add a room to the graph.
        """
        if room_id in self.room_graph:
            print("WARNING: That room already exists")
        else:
            self.room_graph[room_id] = {}

    def add_directions(self, r1, directions):
        """
        Add a directed edge to the graph.
        """
        if r1 in self.room_graph and self.room_graph[r1] == {}:
            real_rooms = directions
            fill_directions = {'n': '?', 's': '?', 'w': '?', 'e': '?'}
            # print("Real rooms: ", real_rooms)
            for i in real_rooms:
                self.room_graph[r1][i] = '?'
            for i in fill_directions:
                if i not in self.room_graph[r1]:
                    self.room_graph[r1][i] = 'X'
            # print("Updated room map to: ",  self.room_graph[r1])
        elif r1 in self.room_graph:
            pass
        else:
            raise IndexError("That room/direction does not exist!")

    def get_rooms(self, room_id, ):
        # print(room_id.get_exits())
        # print(current_room)
        # print("Inside get_rooms...cur room: ", self.room_graph[current_room])
        return room_id.get_exits()



    def dft(self, starting_room, current_room, current_room_exits, s, directions_list):
        # s = Stack()
        # s.push([starting_room])

        # while s.size() > 0:
        print("Current room: ", current_room)
        
        #Normally I'd pop this off...but I don't WANT to, UNLESS no room directions left to explore
        path = s.stack[-1]
        starting_room = path[-1]

        #If new room, initialize in the graph with all '?' values
        if starting_room not in self.room_graph:
            self.add_room(starting_room)
            self.add_directions(starting_room, current_room_exits)
            
        print("Current room's map: ", self.room_graph[current_room])
        # If there are rooms or directions to explore, start exploring!
        if starting_room not in self.room_graph or '?' in list(self.room_graph[current_room].values()):
            #Set current room's map & reset starting_room to current_room
            cur_room_map = self.room_graph[current_room]
            starting_room = current_room
            print("here's what we want to explore: ", cur_room_map)
            #If rooms left to explore...set directions
            if '?' in list(cur_room_map.values()):
                direction = ''
                for i in cur_room_map:
                    if cur_room_map[i] == '?':
                        direction = i
                        break
                opposite_direction = ''
                if direction == 'n':
                    opposite_direction = 's'
                elif direction == 's':
                    opposite_direction = 'n'
                elif direction == 'e':
                    opposite_direction = 'w'
                else:
                    opposite_direction = 'e'


                #### API POST REQUEST ####
                try:
                    response=requests.post(SERVER+'move/', headers=SET_HEADERS, json={"direction":f'{direction}'})
                    print("Server response code: ", response.status_code)
                    response.raise_for_status()
                except HTTPError as http_err:
                    print(f'HTTP error occurred: {http_err}')
                except Exception as err:
                    print(f'Other error occurred: {err}')
                ###LINE 100 WILL NEED TO RECEIVE UPDATE EXITS
                ###THE RESPONSE FROM THIS API REQUEST WILL UPDATE CURRENT_ROOM_EXITS
                r=response.json()
                current_room=r['room_id']
                curr_coordinates=r['coordinates']
                exits=r['exits']
                cooldown=r['cooldown']
                print("ROOM",current_room,curr_coordinates,"VALID EXITS: ",exits,"COOLDOWN: ",cooldown)
                print("TITLE",r['title'],"\nDESC",r['description'],"\nERR:",r['errors'],"\nMSG:",r['messages'],'\n\n')


                # If played switched rooms, map the rooms to my graph
                if current_room != starting_room:
                    # print("Travelled to...", current_room)
                    path = [*path, current_room]
                    # add path to stack
                    s.push(path)

                    # add direction in both rooms to room_graph
                    self.add_room(current_room)             ############
                    self.add_directions(current_room, current_room_exits)
                    self.room_graph[starting_room][direction] = current_room
                    self.room_graph[current_room][opposite_direction] = starting_room
                    print("problem child: ",self.room_graph[starting_room], self.room_graph[current_room])
                    # add direction to directions_list
                    directions_list.append({"direction": f'{direction}'})
                else:
                    # print("Before adding X in else: ", cur_room_map)
                    # add 'X' if direction doesn't lead to a room
                    cur_room_map[direction] = 'X'
        return [current_room, curr_coordinates, exits, cooldown, s, directions_list]

        # pop only after all rooms have been explored
        # s.pop()
        #Hmmmm this is dicey....I'm removing the backwards traversal for right now...just want to see if I can walk around before I think about this.
        # Handle the backward traversal...also the last room in the stack
        # if len(s.stack) != 0:
        #     new_path = s.stack[-1]
        #     new_starting_room = new_path[-1]
        #     for direction, room in self.room_graph[current_room].items():
        #         if room == new_starting_room:
        #             ######API CALL
        #             ####
        #             ####
        #             player.travel(direction)
        #             traversal_path.append(direction)