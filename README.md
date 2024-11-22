# Option Profit Calculator
Option Profit Calculator originally designed for HooHacks 2024. Legacy version powered by Streamlit with data sourced from Alpha Vantage Stock API. Created by Michael Martinez and Alex Zhou from William &amp; Mary and David Hu from the University of Virginia.

Current version powered by PyQt5 with data sourced from the Schwab Developer API. Currently maintained by Michael Martinez. 

## Running the App

To run the app, first clone the repository:
```
git clone https://github.com/mikemartinez13/option-profit-calculator.git
```
Next, create a conda environment with the necessary packages using the `options_proj.yml` file: 
```
conda env create --name options-proj --file=options_proj.yml
```
If you use pip, you can use: 
```
pip install -r requirements.txt
```
Make sure that you have an account setup with [Schwab Developer](https://developer.schwab.com/login). Full instructions for setting up an account can be found in the `project-writeup/writeup.pdf` file. Video instructions can be found on [Tyler Bowers' YouTube](https://www.youtube.com/watch?v=kHbom0KIJwc&ab_channel=TylerBowers). If you do not have a Schwab Developer account, you may still run the app in `demo` mode.

To run the app without Schwab Developer, run:
```
python main.py --demo
```
In your command line. This will open a demo of the app with restricted functionalities using only Apple options data from 11/22/2024.

## Using Schwab Developer

Once you have an active Schwab Developer account and have created an app, open the "Apps Dashboard" in the Schwab Developer Portal. Under your app, press "View Details". In your App Details, copy your App Key and Secret to your clipboard. This will be used to access the API. 
In your `option-profit-calculator` directory, create a file named `.env`, and format it like so: 
```
APP_KEY=<Your App Key>
SECRET_KEY=<Your Secret>
```
Now the program will be able to access your keys and query data from Schwab API. These keys are akin to passwords and __should be kept in a safe location, especially if your Schwab Developer account is connected to your trading account__. The Option Profit Calculator will not store your keys or expose them in any way. 

Once your `.env` file is set up, simply run:
```
python main.py
```
In the command line. The first time you run this, Schwab may ask you to sign in and approve connection to your trading account. This window may appear: 
