#Run this the FIRST TIME ONLY!!!
    # Prompts you to log in to your Schwab brokerage account.
    # Connects brokerage account to developer account.
    # After prompting you to paste a url given to you after login, prints out initial login tokens.

import os
import base64
import requests
import webbrowser
import json
from loguru import logger

def save_tokens_to_file(tokens):
    """Save access and refresh tokens to a JSON file."""
    with open('tokens.json', 'w') as token_file:
        json.dump(tokens, token_file)

def construct_init_auth_url() -> tuple[str, str, str]:
    """Construct the initial URL for Schwab user authentication."""
    app_key = os.getenv("SCHWAB_APP_KEY", 'your-app-key')  # Store app key in environment variables
    app_secret = os.getenv("SCHWAB_APP_SECRET", 'your-app-secret')  # Store app secret in environment variables

    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://127.0.0.1"

    logger.info("Click to authenticate:")
    logger.info(auth_url)

    return app_key, app_secret, auth_url


def construct_headers_and_payload(returned_url, app_key, app_secret):
    """Construct the headers and payload required to exchange authorization code for tokens."""
    response_code = f"{returned_url[returned_url.index('code=') + 5: returned_url.index('%40')]}@"

    credentials = f"{app_key}:{app_secret}"
    base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "grant_type": "authorization_code",
        "code": response_code,
        "redirect_uri": "https://127.0.0.1",
    }

    return headers, payload


def retrieve_tokens(headers, payload) -> dict:
    """Retrieve the initial access and refresh tokens from Schwab API."""
    init_token_response = requests.post(
        url="https://api.schwabapi.com/v1/oauth/token",
        headers=headers,
        data=payload,
    )
    return init_token_response.json()


def run_setup():
    """Run the first-time setup process to authenticate the user and retrieve tokens."""
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

    # Save tokens to environment variables or a secure location
    os.environ['SCHWAB_ACCESS_TOKEN'] = init_tokens_dict['access_token']
    os.environ['SCHWAB_REFRESH_TOKEN'] = init_tokens_dict['refresh_token']

    logger.info("Initial setup completed. Tokens have been stored.")

if __name__ == "__main__":
    run_setup()