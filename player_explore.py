import requests
from dotenv import load_dotenv
import os

load_dotenv()

secret_key=os.getenv("JASON_KEY")

print(secret_key)