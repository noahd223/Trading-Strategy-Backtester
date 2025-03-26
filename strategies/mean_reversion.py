import pandas as pd
import numpy as np

class MeanReversionStrategy:
    def __init__(self, window=20, z_threshold=1.0):
        self.window = window
        self.z_threshold = z_threshold
        
    def generate_signals(self, data):
        """Generate signals based on Bollinger Bands mean reversion"""
        # Ensure we're working with a DataFrame with just the price column
        if isinstance(data, pd.DataFrame):
            df = data[['price']].copy() if 'price' in data.columns else data.iloc[:, [0]].copy().rename(columns={data.columns[0]: 'price'})
        else:
            raise ValueError("Input data must be a pandas DataFrame")
        # Calculate indicators
        df['rolling_mean'] = df['price'].rolling(self.window).mean()
        df['rolling_std'] = df['price'].rolling(self.window).std()
        df['z_score'] = (df['price'] - df['rolling_mean']) / df['rolling_std'].replace(0, np.nan)  # Avoid division by zero
        
        # Generate signals
        df['signal'] = np.select(
            [
                df['z_score'] < -self.z_threshold,
                df['z_score'] > self.z_threshold
            ],
            [
                1,  # Buy
                -1  # Sell
            ],
            default=0  # Neutral
        )
        df['signal'] = df['signal'].shift(1)
        return df.dropna()
    
    def calculate_returns(self, data_with_signals):
        """Calculate strategy returns"""
        df = data_with_signals.copy()
        df['daily_returns'] = df['price'].pct_change()
        df['strategy_returns'] = df['signal'] * df['daily_returns']
        return df