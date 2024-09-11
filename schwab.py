import requests
import base64
import urllib.parse
import json

# taken from Tyler Bowers on YouTube

appKey = 'Your app key'
appSecret = 'Your secret key'

authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={appKey}&redirect_uri=https://127.0.0.1'

print(f"Click to authenticate: {authUrl}")

returnedLink = input("Paste the redirect URL here:")

code = f"{returnedLink[returnedLink.index('code=')+5:returnedLink.index('%40')]}@"

headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{appKey}:{appSecret}", "utf-8")).decode("utf-8")}','Content-Type': 'application/x-www-form-urlencoded'}

data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': 'https://127.0.0.1'}

response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
tD = response.json()
print(tD)

access_token = tD['access_token'] # valid for 30 minutes
refresh_token = tD['refresh_token'] # valid for 7 days, used to get a new access token

# Example request 

base_url = 'https://api.schwabapi.com/trader/v1/'

response = requests.get(f'{base_url}/accounts/accountNumbers', headers={'Authorization': f'Bearer {access_token}'})
#print(response.ok())

print(response.json())

base_api_url = "https://api.schwabapi.com"

def _params_parser(params):
    """
    Removes None (null) values
    :param params: params to remove None values from
    :type params: dict
    :return: params without None values
    :rtype: dict
    """
    for key in list(params.keys()):
        if params[key] is None: del params[key]
    return params

# Get Market Data for AMZN
response = requests.get(f'{base_api_url}/marketdata/v1/{urllib.parse.quote("AMZN")}/quotes',
                            headers={'Authorization': f'Bearer {access_token}'},
                            params=_params_parser({'fields': ["all"]}),
                            timeout=5)

print(response.json())
