import matplotlib.pyplot as plt
import numpy as np
from data.data import get_historical_data
from strategies.moving_average import MovingAverageStrategy
from strategies.mean_reversion import MeanReversionStrategy


def get_strategy_choice():
    """Prompt user to select a strategy"""
    print("\nAvailable Strategies:")
    print("1. Moving Average Crossover (50/200)")
    print("2. Mean Reversion (Bollinger Bands)")
    print("3. Compare Both Strategies")
    print("4. Exit")
    
    while True:
        try:
            choice = int(input("Select strategy (1-3) or Exit (4): "))
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
        # Price and indicators plot
        results['price'].plot(label='Price', alpha=0.5)
        
        if 'MA_50' in results.columns:  # Moving Average strategy
            results['MA_50'].plot(label='50-day MA')
            results['MA_200'].plot(label='200-day MA')
        elif 'rolling_mean' in results.columns:  # Mean Reversion strategy
            results['rolling_mean'].plot(label=f'{results.attrs["window"]}-day Mean')
            upper = results['rolling_mean'] + results.attrs["z_threshold"]*results['rolling_std']
            lower = results['rolling_mean'] - results.attrs["z_threshold"]*results['rolling_std']
            upper.plot(label='Upper Band', linestyle='--', alpha=0.5)
            lower.plot(label='Lower Band', linestyle='--', alpha=0.5)
        
        buy_signals = results[results['signal'] == 1]
        sell_signals = results[results['signal'] == -1]
        plt.scatter(buy_signals.index, buy_signals['price'], marker='^', color='g', label='Buy')
        plt.scatter(sell_signals.index, sell_signals['price'], marker='v', color='r', label='Sell')
        
        plt.title(f"{strategy_name} Trading Signals")
        plt.legend()
        plt.show()

def run_comparison(data):
    """Compare both strategies"""
    # Initialize strategies
    ma_strategy = MovingAverageStrategy(50, 200)
    mr_strategy = MeanReversionStrategy(20, 1.0)
    
    # Run strategies
    ma_results = ma_strategy.calculate_returns(ma_strategy.generate_signals(data))
    mr_results = mr_strategy.calculate_returns(mr_strategy.generate_signals(data))
    
    # Store metadata for plotting
    ma_results.attrs = {"strategy": "Moving Average"}
    mr_results.attrs = {"strategy": "Mean Reversion", "window": 20, "z_threshold": 1.0}
    
    # Evaluate
    ma_return = evaluate_performance(ma_results, "Moving Average (50/200)")
    mr_return = evaluate_performance(mr_results, "Mean Reversion (Bollinger Bands)")
    
    # Plot comparison
    plt.figure(figsize=(14, 6))
    (1 + data['price'].pct_change()).cumprod().plot(label='Buy & Hold')
    (1 + ma_results['strategy_returns']).cumprod().plot(label='MA Strategy')
    (1 + mr_results['strategy_returns']).cumprod().plot(label='MR Strategy')
    plt.title("Strategy Comparison")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return ma_return, mr_return

if __name__ == "__main__":
    # Fetch data
    data = get_historical_data('SPY')
    
    # Get user input
    choice = get_strategy_choice()
    
    if choice == 1:  # Moving Average
        strategy = MovingAverageStrategy(50, 200)
        results = strategy.calculate_returns(strategy.generate_signals(data))
        results.attrs = {"strategy": "Moving Average"}
        evaluate_performance(results, "Moving Average (50/200)")
        plot_results(results, "Moving Average")
        
    elif choice == 2:  # Mean Reversion
        strategy = MeanReversionStrategy(20, 1.0)
        results = strategy.calculate_returns(strategy.generate_signals(data))
        results.attrs = {"strategy": "Mean Reversion", "window": 20, "z_threshold": 1.0}
        evaluate_performance(results, "Mean Reversion (Bollinger Bands)")
        plot_results(results, "Mean Reversion")
        
    elif choice == 3:  # Compare both
        run_comparison(data)