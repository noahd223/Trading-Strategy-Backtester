import matplotlib.pyplot as plt
import numpy as np
from data.data import get_historical_data
from strategies.moving_average import MovingAverageStrategy
from strategies.rsi import RSIStrategy  # Changed from MeanReversionStrategy

def get_strategy_choice():
    """Prompt user to select a strategy"""
    print("\nAvailable Strategies:")
    print("1. Moving Average Crossover (50/200)")
    print("2. RSI Strategy (30/70)")  # Updated label
    print("3. Compare Both Strategies")
    print("4. Exit")
    
    while True:
        try:
            choice = int(input("Select strategy (1-4): "))
            if 1 <= choice <= 4:
                return choice
            print("Please enter 1, 2, 3, or 4")
        except ValueError:
            print("Invalid input. Please enter a number.")

def evaluate_performance(df, strategy_name):
    """Evaluate and print performance metrics"""
    cumulative_returns = (1 + df['strategy_returns']).cumprod()
    total_return = cumulative_returns.iloc[-1] - 1
    
    sharpe = np.sqrt(252) * (df['strategy_returns'].mean() / df['strategy_returns'].std())
    
    peak = cumulative_returns.cummax()
    max_drawdown = (cumulative_returns - peak).min()
    
    print(f"\n{strategy_name} Performance:")
    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2%}")
    return total_return

def plot_results(results, strategy_name, show_signals=True):
    """Visualize strategy performance"""
    # Cumulative returns plot
    plt.figure(figsize=(14, 6))
    (1 + results['daily_returns']).cumprod().plot(label='Buy & Hold')
    (1 + results['strategy_returns']).cumprod().plot(label=f'{strategy_name} Strategy')
    plt.title(f"{strategy_name} Strategy Performance")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    if show_signals:
        # Create figure with subplots
        is_rsi_strategy = 'rsi' in results.columns
        if is_rsi_strategy:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        else:
            fig, ax1 = plt.subplots(figsize=(14, 6))
        
        # Price and MA plot (top subplot)
        results['price'].plot(ax=ax1, label='Price', alpha=0.5)
        
        if 'MA_50' in results.columns:  # Moving Average strategy
            results['MA_50'].plot(ax=ax1, label='50-day MA')
            results['MA_200'].plot(ax=ax1, label='200-day MA')
        elif 'ma' in results.columns:  # RSI strategy
            results['ma'].plot(ax=ax1, label=f'{results.attrs.get("trend_window", 200)}-day MA', color='orange')
        
        # Plot buy/sell signals
        buy_signals = results[results['signal'] == 1]
        sell_signals = results[results['signal'] == -1]
        ax1.scatter(buy_signals.index, buy_signals['price'], marker='^', color='g', label='Buy')
        ax1.scatter(sell_signals.index, sell_signals['price'], marker='v', color='r', label='Sell')
        
        ax1.set_title(f"{strategy_name} Trading Signals")
        ax1.legend()
        ax1.grid(True)
        
        # RSI plot (bottom subplot)
        if 'rsi' in results.columns:
            results['rsi'].plot(ax=ax2, label='RSI', color='purple')
            ax2.axhline(70, linestyle='--', color='r', alpha=0.5)
            ax2.axhline(30, linestyle='--', color='g', alpha=0.5)
            ax2.set_ylabel('RSI')
            ax2.grid(True)
            
        
        plt.tight_layout()
        plt.show()

def run_comparison(data):
    """Compare both strategies"""
    # Initialize strategies
    ma_strategy = MovingAverageStrategy(50, 200)
    rsi_strategy = RSIStrategy(oversold=30, overbought=70, window=14)  # Updated
    
    # Run strategies
    ma_results = ma_strategy.calculate_returns(ma_strategy.generate_signals(data))
    rsi_results = rsi_strategy.calculate_returns(rsi_strategy.generate_rsi_signals(data))  # Updated method name
    
    # Store metadata for plotting
    ma_results.attrs = {"strategy": "Moving Average"}
    rsi_results.attrs = {"strategy": "RSI"}
    
    # Evaluate
    ma_return = evaluate_performance(ma_results, "Moving Average (50/200)")
    rsi_return = evaluate_performance(rsi_results, "RSI Strategy (30/70)")
    
    # Plot comparison
    plt.figure(figsize=(14, 6))
    (1 + data['price'].pct_change()).cumprod().plot(label='Buy & Hold')
    (1 + ma_results['strategy_returns']).cumprod().plot(label='MA Strategy')
    (1 + rsi_results['strategy_returns']).cumprod().plot(label='RSI Strategy')
    plt.title("Strategy Comparison")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return ma_return, rsi_return

if __name__ == "__main__":
    # Fetch data
    data = get_historical_data('SPY')
    
    # Get user input
    choice = get_strategy_choice()
    
    if choice == 1:  # Moving Average
        # Get user input for MA parameters
        print("\nConfigure Moving Average Strategy Parameters:")
        while True:
            try:
                short_window = int(input("Enter short MA window (default 50): ") or 50)
                long_window = int(input("Enter long MA window (default 200): ") or 200)
                
                if short_window >= long_window:
                    print("Short window must be less than long window")
                    continue
                if short_window <= 0 or long_window <= 0:
                    print("Window values must be positive")
                    continue
                break
            except ValueError:
                print("Please enter valid numbers")
        
        strategy = MovingAverageStrategy(short_window=short_window, long_window=long_window)
        results = strategy.calculate_returns(strategy.generate_signals(data))
        results.attrs = {
            "strategy": "Moving Average",
            "short_window": short_window,
            "long_window": long_window
        }
        strategy_name = f"Moving Average ({short_window}/{long_window})"
        evaluate_performance(results, strategy_name)
        plot_results(results, strategy_name)
        
    elif choice == 2:  # RSI Strategy
        # Get user input for RSI parameters
        print("\nConfigure RSI Strategy Parameters:")
        while True:
            try:
                oversold = int(input("Enter oversold threshold (default 30): ") or 30)
                overbought = int(input("Enter overbought threshold (default 70): ") or 70)
                window = int(input("Enter RSI window (default 14): ") or 14)
                trend_window = int(input("Enter trend MA window (default 200): ") or 200)
                
                if oversold >= overbought:
                    print("Oversold must be less than overbought")
                    continue
                if window <= 0 or trend_window <= 0:
                    print("Window values must be positive")
                    continue
                break
            except ValueError:
                print("Please enter valid numbers")
        
        strategy = RSIStrategy(oversold=oversold, overbought=overbought, 
                             window=window, trend_window=trend_window)
        results = strategy.calculate_returns(strategy.generate_rsi_signals(data))
        results.attrs = {
            "strategy": "RSI",
            "trend_window": trend_window
        }
        strategy_name = f"RSI Strategy ({oversold}/{overbought}, {window} day)"
        evaluate_performance(results, strategy_name)
        plot_results(results, strategy_name)
        
    elif choice == 3:  # Compare both
        run_comparison(data)