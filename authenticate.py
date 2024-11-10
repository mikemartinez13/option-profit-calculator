# Easy authentication using the schwabdev package. 
# Ported directly from Tyler E. Bowers' implementation at https://pypi.org/project/schwabdev/

import schwabdev #import the package
import os
from dotenv import load_dotenv

load_dotenv()

app_key = os.getenv('APP_KEY')
secret = os.getenv('SECRET_KEY')

client = schwabdev.Client(app_key, secret)  #create a client

print(client.account_linked().json()) # prints the account linked to the client