import pandas as pd
import numpy as np

class MovingAverageStrategy:
    def __init__(self, short_window=50, long_window=200):
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signals(self, data):
        """Generate trading signals based on MA crossover"""
        df = data.copy()
        
        # Calculate moving averages
        df[f'MA_{self.short_window}'] = df['price'].rolling(self.short_window).mean()
        df[f'MA_{self.long_window}'] = df['price'].rolling(self.long_window).mean()
        
        # Generate signals (1 = buy, -1 = sell)
        df['signal'] = np.where(
            df[f'MA_{self.short_window}'] > df[f'MA_{self.long_window}'], 
            1, 
            -1
        )
        df['signal'] = df['signal'].shift(1)  # Avoid look-ahead bias
        
        return df.dropna()
    
    def calculate_returns(self, data_with_signals):
        """Calculate strategy returns"""
        df = data_with_signals.copy()
        df['daily_returns'] = df['price'].pct_change()
        df['strategy_returns'] = df['signal'] * df['daily_returns']
        return df