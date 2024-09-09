from math_utils.black_scholes import BlackScholesCalculator
from visualizations.pricing_visualizer import PricingMatrixVisualizer
from data.data_manager import DataManager
import pandas as pd

def main():
    # Initialize components
    stock_price = 100
    time_to_maturity = 1
    risk_free_rate = 0.05
    volatility = 0.2
    strikes = [80, 90, 100, 110, 120]

    # Black-Scholes Calculator
    bs_calculator = BlackScholesCalculator(stock_price, time_to_maturity, risk_free_rate, volatility)
    
    # Create a pricing table
    table_data = []
    for K in strikes:
        call_price = bs_calculator.calculate(K, option_type='call')
        put_price = bs_calculator.calculate(K, option_type='put')
        table_data.append({'Strike Price': K, 'Call Price': round(call_price, 2), 'Put Price': round(put_price, 2)})
    
    pricing_table = pd.DataFrame(table_data)
    
    # Visualize the pricing matrix
    visualizer = PricingMatrixVisualizer(pricing_table)
    visualizer.plot()

if __name__ == "__main__":
    main()
