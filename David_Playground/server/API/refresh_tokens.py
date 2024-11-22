# Script to fetch, replace, and generate a refresher token and authorization token every 30 minutes. This ensures a working token always.

import os
import base64
import requests
import time
import threading
from loguru import logger
import json

# xtra method
def save_tokens_to_file(tokens):
    """Save access and refresh tokens to a JSON file."""
    with open('tokens.json', 'w') as token_file:
        json.dump(tokens, token_file)

def refresh_tokens():
    """Fetch and refresh Schwab tokens using the refresh token."""
    logger.info("Initializing token refresh...")

    # Load app key, app secret, and refresh token from environment variables or a secure storage
    app_key = os.getenv('SCHWAB_APP_KEY', 'your-app-key')
    app_secret = os.getenv('SCHWAB_APP_SECRET', 'your-app-secret')
    refresh_token_value = os.getenv('SCHWAB_REFRESH_TOKEN', 'your-current-refresh-token')

    # Construct the payload and headers
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value,
    }
    headers = {
        "Authorization": f'Basic {base64.b64encode(f"{app_key}:{app_secret}".encode()).decode()}',
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Send the request to refresh tokens
    refresh_token_response = requests.post(
        url="https://api.schwabapi.com/v1/oauth/token",
        headers=headers,
        data=payload,
    )

    if refresh_token_response.status_code == 200:
        logger.info("Retrieved new tokens successfully using refresh token.")
    else:
        logger.error(f"Error refreshing access token: {refresh_token_response.text}")
        return None

    # Parse the new tokens
    refresh_token_dict = refresh_token_response.json()
    logger.debug(refresh_token_dict)

    # Update the environment variables or store them securely
    os.environ['SCHWAB_ACCESS_TOKEN'] = refresh_token_dict['access_token']
    os.environ['SCHWAB_REFRESH_TOKEN'] = refresh_token_dict['refresh_token']
    
    logger.info("Tokens have been refreshed and updated.")

    # After retrieving the tokens, store them "securely" in local json file
    if refresh_token_response.status_code == 200:
        refresh_token_dict = refresh_token_response.json()
        
        # Save tokens to a file
        save_tokens_to_file(refresh_token_dict)

        # Log the success
        logger.info("Tokens have been refreshed and saved to file.")

    return refresh_token_dict

def start_token_refresh():
    """Continuously refresh the token every 30 minutes."""
    while True:
        refresh_tokens()
        time.sleep(1800)  # Sleep for 30 minutes (1800 seconds)

def run_background_token_refresh():
    """Start the token refresh process as a background thread."""
    refresh_thread = threading.Thread(target=start_token_refresh)
    refresh_thread.daemon = True  # Daemonize thread to stop with the app
    refresh_thread.start()
