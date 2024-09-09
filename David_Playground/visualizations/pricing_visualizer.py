import seaborn as sns
import matplotlib.pyplot as plt

class PricingMatrixVisualizer:
    def __init__(self, df):
        self.df = df
    
    def plot(self):
        plt.figure(figsize=(10, 6))
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

        sns.heatmap(self.df.pivot(index='Strike Price', columns='Call Price', values='Call Price'),
                    annot=True, fmt=".2f", cmap='Blues', ax=axes[0])
        axes[0].set_title('Call Option Prices')
        
        sns.heatmap(self.df.pivot(index='Strike Price', columns='Put Price', values='Put Price'),
                    annot=True, fmt=".2f", cmap='Reds', ax=axes[1])
        axes[1].set_title('Put Option Prices')

        plt.tight_layout()
        plt.show()