import schwabdev 
import requests
import os
import time
import json
import pandas as pd


appKey = 'Your app key here'
appSecret = 'Your secret key here'

def main():
    # place your app key and app secret in the .env file
    #load_dotenv()  # load environment variables from .env file

    client = schwabdev.Client(appKey, appSecret, 'https://127.0.0.1')

    # define a variable for the steamer:
    streamer = client.stream

    # example of using your own response handler, prints to main terminal.
    # the first parameter is used by the stream, additional parameters are passed to the handler
    def my_handler(message):
        print("test_handler:" + message)

    #streamer.start(my_handler)


    # start steamer with default response handler (print):
    #streamer.start()

    """
    You can stream up to 500 keys.
    By default all shortcut requests (below) will be "ADD" commands meaning the list of symbols will be added/appended 
    to current subscriptions for a particular service, however if you want to overwrite subscription (in a particular 
    service) you can use the "SUBS" command. Unsubscribing uses the "UNSUBS" command. To change the list of fields use
    the "VIEW" command.
    """
    print(client.quotes('AAPL', 'all').json())
    print(client.option_expiration_chain('AAPL').json())
    print(client.option_chains('AAPL').json())

    #q: How can I write the AAPL options chain to a .json file?
    # a:    
    #q: How do I make the output have nice indentations? 
    # a: use the indent parameter in json.dump
    # 

    with open('AAPL_options_chain.json', 'w') as f:
        json.dump(client.option_chains('AAPL').json(), f, indent=4)
        f.close()
    
    aapl_data = pd.DataFrame(client.option_chains('AAPL').json())
    print(aapl_data)

    # these three do the same thing
    # streamer.send(streamer.basic_request("LEVELONE_EQUITIES", "ADD", parameters={"keys": "AMD,INTC", "fields": "0,1,2,3,4,5,6,7,8"}))
    # streamer.send(streamer.level_one_equities("AMD,INTC", "0,1,2,3,4,5,6,7,8", command="ADD"))

    #streamer.send(streamer.level_one_equities("AMD,INTC", "0,1,2,3,4,5,6,7,8"))


    #streamer.send(streamer.level_one_options("GOOGL 240712C00200000", "0,1,2,3,4,5,6,7,8")) # key must be from option chains api call.

    #streamer.send(streamer.level_one_futures("/ES", "0,1,2,3,4,5,6"))

    # streamer.send(streamer.level_one_futures_options("./OZCZ23C565", "0,1,2,3,4,5"))

    #streamer.send(streamer.level_one_forex("EUR/USD", "0,1,2,3,4,5,6,7,8"))

    #streamer.stop()

    # streamer.send(streamer.nyse_book(["F", "NIO"], "0,1,2,3,4,5,6,7,8"))

    # streamer.send(streamer.nasdaq_book("AMD", "0,1,2,3,4,5,6,7,8"))

    # streamer.send(streamer.options_book("GOOGL 240712C00200000", "0,1,2,3,4,5,6,7,8"))

    # streamer.send(streamer.chart_equity("AMD", "0,1,2,3,4,5,6,7,8"))

    # streamer.send(streamer.chart_futures("/ES", "0,1,2,3,4,5,6,7,8"))

    # streamer.send(streamer.screener_equity("NASDAQ_VOLUME_30", "0,1,2,3,4,5,6,7,8"))

    # streamer.send(streamer.screener_options("OPTION_CALL_TRADES_30", "0,1,2,3,4,5,6,7,8"))

    # streamer.send(streamer.account_activity("Account Activity", "0,1,2,3"))


    # stop the stream after 60 seconds (since this is a demo)
    # time.sleep(10)
    # streamer.stop()
    # if you don't want to clear the subscriptions, set clear_subscriptions=False
    # streamer.stop(clear_subscriptions=False)


if __name__ == '__main__':
    print("Welcome to the unofficial Schwab interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    main()  # call the user code above