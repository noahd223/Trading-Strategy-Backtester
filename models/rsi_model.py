# to test this model follow instructions at the bottom and then look at rsi_tester.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer
from data.data import get_historical_data
from strategies.rsi import RSIStrategy

# Define function to calculate strategy returns
def calculate_strategy_return(oversold, overbought, window, trend_window, data):
    strategy = RSIStrategy(
        oversold=oversold,
        overbought=overbought,
        window=window,
        trend_window=trend_window
    )
    signals = strategy.generate_rsi_signals(data)
    results = strategy.calculate_returns(signals)
    return (1 + results['strategy_returns']).cumprod()

# Load dataset
data = get_historical_data('SPY')

# Define parameter grid
param_grid = {
    'oversold': np.arange(10, 40),          # RSI 10-39
    'overbought': np.arange(55, 95),        # RSI 55-94
    'window': np.arange(3, 40),             # Window 3-39
    'trend_window': np.arange(50, 500, 10)  # MA 50-490
}

# Generate training data
param_samples = pd.DataFrame({
    'oversold': np.random.choice(param_grid['oversold'], 100),
    'overbought': np.random.choice(param_grid['overbought'], 100),
    'window': np.random.choice(param_grid['window'], 100),
    'trend_window': np.random.choice(param_grid['trend_window'], 100)
})

returns_list = []
for _, row in param_samples.iterrows():
    returns_list.append(calculate_strategy_return(
        row['oversold'], row['overbought'], row['window'], row['trend_window'], data)
    )

param_samples['return'] = [r.iloc[-1] - 1 for r in returns_list]

# Prepare features and target
X = param_samples.drop(columns=['return'])
y = param_samples['return']

# Define Random Forest model
rf = RandomForestRegressor()

# Define a scorer function for maximizing returns
def return_scorer(y_true, y_pred):
    return np.mean(y_true)  # Optimizing for highest REAL backtested return

# Use make_scorer with the corrected function
custom_scorer = make_scorer(return_scorer, greater_is_better=True)

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
}

grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=TimeSeriesSplit(n_splits=3),
    scoring=custom_scorer,
    n_jobs=-1
)

grid_search.fit(X, y)
print("Best Parameters:", grid_search.best_params_)
print(f"Best estimated return: {grid_search.best_score_:.2%}")

# Train final model with best parameters
best_rf = grid_search.best_estimator_
predicted_returns = best_rf.predict(X)

# Select best RSI parameters
best_index = np.argmax(predicted_returns)
best_params = X.iloc[best_index].to_dict()
print("Best RSI parameters:", best_params)

# Backtest using best parameters
best_strategy = RSIStrategy(**best_params)
signals = best_strategy.generate_rsi_signals(data)
results = best_strategy.calculate_returns(signals)

# Calculate cumulative returns
optimized_return = (1 + results['strategy_returns']).cumprod().iloc[-1] - 1
buy_hold_return = (1 + results['daily_returns']).cumprod().iloc[-1] - 1
return_difference = (optimized_return - buy_hold_return) / abs(buy_hold_return) # use percent change formula

print(f"Optimized Strategy Return: {optimized_return:.2%}")
print(f"Buy & Hold Return: {buy_hold_return:.2%}")
print(f"Return Difference: {return_difference:.2%}")

# Plot results for every iteration
plt.figure(figsize=(12, 6))
for r in returns_list:
    plt.plot(r.index, r, color='lightgray', alpha=0.5, linewidth=1)
(1 + results['strategy_returns']).cumprod().plot(label='Optimized Strategy', color='blue', linewidth=2)
(1 + results['daily_returns']).cumprod().plot(label='Buy & Hold', color='green', linewidth=2)
plt.title(f"Best Parameters: {best_params}")
plt.legend()
plt.show() # comment this out if using rsi_tester.py
# uncomment if using rsi_tester.py so that graph closes automatically
#plt.show(block=False) 