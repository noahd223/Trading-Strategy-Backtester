import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, oversold=30, overbought=70, window=14, trend_window=200):
        self.oversold = oversold
        self.overbought = overbought
        self.window = window
        self.trend_window = trend_window

    def calculate_rsi(self, data):
        """Calculate RSI with bounds handling."""
        delta = data['price'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.ewm(alpha=1/self.window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.window, adjust=False).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return np.clip(100 - (100 / (1 + rs)), 0, 100)

    def generate_rsi_signals(self, data):
        """Generate signals with proper position tracking."""
        # Handle MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data = data.copy()
            data.columns = data.columns.get_level_values(0)
        
        df = data.copy()
        df['rsi'] = self.calculate_rsi(df)
        df['ma'] = df['price'].rolling(self.trend_window).mean()
        
        # Initialize columns
        df['signal'] = 0
        df['position'] = 0
        
        # Vectorized conditions
        buy_condition = (df['rsi'] < self.oversold) & (df['price'] > df['ma'])
        sell_condition = (df['rsi'] > self.overbought)
        
        # Initialize position tracking
        position = 0
        positions = []
        
        for i in range(len(df)):
            if buy_condition.iloc[i] and position == 0:
                df.loc[df.index[i], 'signal'] = 1
                position = 1
            elif sell_condition.iloc[i] and position == 1:
                df.loc[df.index[i], 'signal'] = -1
                position = 0
            positions.append(position)
        
        df['position'] = positions
        df['signal'] = df['signal'].shift(1)  # Avoid look-ahead
        return df.dropna()

    def calculate_returns(self, data_with_signals):
        """Calculate returns based on position."""
        df = data_with_signals.copy()
        df['daily_returns'] = df['price'].pct_change()
        
        # Calculate strategy returns (1 when long, 0 when flat)
        df['strategy_returns'] = df['position'].shift(1) * df['daily_returns']
        
        # Handle potential NaN in returns
        df['strategy_returns'] = df['strategy_returns'].fillna(0)
        return df