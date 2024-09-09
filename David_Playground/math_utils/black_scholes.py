import numpy as np
import scipy.stats as stats

class BlackScholesCalculator:
    def __init__(self, S, T, r, sigma):
        self.S = S
        self.T = T
        self.r = r
        self.sigma = sigma

    def calculate(self, K, option_type='call'):
        d1 = (np.log(self.S / K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)

        if option_type == 'call':
            return (self.S * stats.norm.cdf(d1)) - (K * np.exp(-self.r * self.T) * stats.norm.cdf(d2))
        elif option_type == 'put':
            return (K * np.exp(-self.r * self.T) * stats.norm.cdf(-d2)) - (self.S * stats.norm.cdf(-d1))
        else:
            raise ValueError("Invalid option type. Use 'call' or 'put'.")