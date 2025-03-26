class MovingAverageStrategy:
    def __init__(self, short_window=50, long_window=200):
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signals(self, data):
        """Generate trading signals with position maintenance"""
        df = data.copy()
        
        # Calculate moving averages
        df[f'MA_{self.short_window}'] = df['price'].rolling(self.short_window).mean()
        df[f'MA_{self.long_window}'] = df['price'].rolling(self.long_window).mean()
        
        # Initialize columns
        df['signal'] = 0  # 1 for buy, -1 for sell
        df['position'] = 0  # 1 when long, 0 when flat
        
        # Vectorized conditions
        buy_condition = df[f'MA_{self.short_window}'] > df[f'MA_{self.long_window}']
        sell_condition = df[f'MA_{self.short_window}'] <= df[f'MA_{self.long_window}']
        
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
        """Calculate returns based on position"""
        df = data_with_signals.copy()
        df['daily_returns'] = df['price'].pct_change()
        
        # Returns are generated while in position (position = 1)
        df['strategy_returns'] = df['position'].shift(1) * df['daily_returns']
        
        # Handle potential NaN in returns
        df['strategy_returns'] = df['strategy_returns'].fillna(0)
        return df