from flask import Flask, render_template, request
from math_utils.black_scholes import BlackScholesCalculator
from server.API.refresh_tokens import run_background_token_refresh
from server.API.setup import run_setup
import os
import json

app = Flask(__name__, template_folder=os.path.join('server', 'templates'))

def load_tokens_from_file():
    """Load tokens from a file (JSON) and set them as environment variables."""
    if os.path.exists('tokens.json'):
        with open('tokens.json', 'r') as token_file:
            tokens = json.load(token_file)
            os.environ['SCHWAB_ACCESS_TOKEN'] = tokens['access_token']
            os.environ['SCHWAB_REFRESH_TOKEN'] = tokens['refresh_token']
            return True
    return False

@app.before_first_request
def initialize_app():
    """Initialize the app: start the token refresh background process or run setup."""
    # Try to load tokens from a file or environment
    tokens_exist = load_tokens_from_file()

    # If no tokens exist, run the setup script to get them
    if not tokens_exist or not os.getenv('SCHWAB_ACCESS_TOKEN') or not os.getenv('SCHWAB_REFRESH_TOKEN'):
        run_setup()  # Trigger the setup process (OAuth login flow)
    
    # Start background refresh process
    run_background_token_refresh()

# Route for the home page (index)
@app.route('/')
def home():
    return render_template('index.html')

# Route for the Black-Scholes calculator form page
@app.route('/calculate', methods=['GET'])
def calculate_option_form():
    return render_template('calculator.html')

# Route to handle pricing after receiving the stock ticker
@app.route('/pricing', methods=['POST'])
def pricing_matrix():
    stock_ticker = request.form['stock_ticker'].upper()

    # Assume we have some logic to get the stock price for the given ticker
    # For simplicity, we will assume a fixed stock price (e.g., 150)
    stock_price = 150  # In a real app, you'd get this from an API like Yahoo Finance or Alpha Vantage

    # Example range of strike prices
    strike_prices = [stock_price - 20, stock_price - 10, stock_price, stock_price + 10, stock_price + 20]
    time_to_maturity = 1  # Assume 1 year to maturity
    risk_free_rate = 0.05  # Assume a 5% risk-free rate
    volatility = 0.2  # Assume 20% volatility

    # Generate the option pricing matrix for each strike price
    pricing_matrix = []
    calculator = BlackScholesCalculator(stock_price, time_to_maturity, risk_free_rate, volatility)

    for strike_price in strike_prices:
        call_price = calculator.calculate(strike_price, option_type='call')
        put_price = calculator.calculate(strike_price, option_type='put')
        pricing_matrix.append({
            'strike_price': strike_price,
            'call_price': round(call_price, 2),
            'put_price': round(put_price, 2)
        })

    # Render the pricing result page with the calculated prices
    return render_template('pricing.html', stock_ticker=stock_ticker, stock_price=stock_price, pricing_matrix=pricing_matrix)

if __name__ == "__main__":  
    app.run(debug=True)