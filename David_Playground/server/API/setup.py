import base64
import requests
import webbrowser
import sys
from urllib.parse import urlparse, parse_qs
from loguru import logger
from config import SCHWAB_API_SECRET, SCHWAB_API_KEY

def construct_init_auth_url():
    try:
        app_key = SCHWAB_API_KEY
        app_secret = SCHWAB_API_SECRET
        auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://b6fb-199-111-225-52.ngrok-free.app"
        
        logger.info("Constructed authentication URL.")
        return app_key, app_secret, auth_url
    except Exception as e:
        logger.error(f"Error in construct_init_auth_url: {e}")
        raise

def construct_headers_and_payload(returned_url, app_key, app_secret):
    try:
        # Parse the returned URL to extract the 'code' parameter
        response_code = parse_qs(urlparse(returned_url).query)['code'][0]
        
        credentials = f"{app_key}:{app_secret}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        payload = {
            "grant_type": "authorization_code",
            "code": response_code,
            "redirect_uri": "https://b6fb-199-111-225-52.ngrok-free.app",  # Match the auth URL
        }

        logger.info("Constructed headers and payload.")
        return headers, payload
    except Exception as e:
        logger.error(f"Error in construct_headers_and_payload: {e}")
        raise

def retrieve_tokens(headers, payload):
    try:
        init_token_response = requests.post(
            url="https://api.schwabapi.com/v1/oauth/token",
            headers=headers,
            data=payload,
        )

        if init_token_response.status_code != 200:
            logger.error(f"Token retrieval failed. Status Code: {init_token_response.status_code}, Headers: {init_token_response.headers}, Response: {init_token_response.text}")
            raise Exception(f"Failed to retrieve tokens: {init_token_response.text}")

        init_tokens_dict = init_token_response.json()
        logger.info("Successfully retrieved tokens.")
        return init_tokens_dict
    except Exception as e:
        logger.error(f"Error in retrieve_tokens: {e}")
        raise

def run_setup():
    """Run the first-time setup process to authenticate the user and retrieve tokens."""
    try:
        app_key, app_secret, cs_auth_url = construct_init_auth_url()
        webbrowser.open(cs_auth_url)

        logger.info("Paste Returned URL:")
        returned_url = input()  # User pastes the URL returned by Schwab after login

        init_token_headers, init_token_payload = construct_headers_and_payload(
            returned_url, app_key, app_secret
        )

        init_tokens_dict = retrieve_tokens(
            headers=init_token_headers, payload=init_token_payload
        )

        logger.debug(init_tokens_dict)

        # Save tokens to local file config.py
        with open("config.py", "w") as f:
            f.write(f'SCHWAB_ACCESS_TOKEN = "{init_tokens_dict["access_token"]}"\n')
            f.write(f'SCHWAB_REFRESH_TOKEN = "{init_tokens_dict["refresh_token"]}"\n')

        logger.info("Initial setup completed. Tokens have been saved to config.py.")

    except Exception as e:
        logger.error(f"Error during setup process: {e}")
        raise

if __name__ == "__main__":
    logger.add(sys.stdout, level="DEBUG")
    print("setup starting")
    run_setup()
