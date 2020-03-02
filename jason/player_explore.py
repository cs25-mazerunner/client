import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

secret_key=os.getenv("JASON_KEY")

requests.get('https://api.github.com')

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
response =requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/',f'Authorization: Token {secret_key}')
#pull relevant values
curr_room=response.room_id
curr_coordinates=response.coordinates
exits=response.exits
cooldown=response.cooldown

#Start walk loop
while True:
    

    break