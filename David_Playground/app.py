from flask import Flask, render_template, request
from math_utils.black_scholes import BlackScholesCalculator
import os

# Set the template_folder to point to 'server/templates' so Flask can find the templates through server logic
app = Flask(__name__, template_folder=os.path.join('server', 'templates'))

@app.route('/')
def home():
    return render_template('index.html')

# Route for the Black-Scholes calculator form page
@app.route('/calculator', methods=['GET', 'POST'])
def calculate_option():
    if request.method == 'POST':
        stock_price = float(request.form['stock_price'])
        strike_price = float(request.form['strike_price'])
        time_to_maturity = float(request.form['time_to_maturity'])
        risk_free_rate = float(request.form['risk_free_rate'])
        volatility = float(request.form['volatility'])
        option_type = request.form['option_type']

        # Use Black-Scholes Calculator
        calculator = BlackScholesCalculator(stock_price, time_to_maturity, risk_free_rate, volatility)
        option_price = calculator.calculate(strike_price, option_type)

        # Render result page with option price
        return render_template('pricing.html', option_price=option_price)

    # If GET request, render the form page
    return render_template('calculator.html')

# Route for the Pricing Matrix page
@app.route('/pricing')
def pricing_matrix():
    # Sample data for now; you can add logic to generate a pricing matrix later
    sample_matrix = [
        {'strike_price': 80, 'call_price': 25.35, 'put_price': 1.90},
        {'strike_price': 90, 'call_price': 17.81, 'put_price': 3.51},
        {'strike_price': 100, 'call_price': 11.34, 'put_price': 6.04}
    ]

    return render_template('pricing.html', matrix=sample_matrix)

if __name__ == "__main__":
    app.run(debug=True)