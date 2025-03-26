import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
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
    return (1 + results['strategy_returns']).cumprod().iloc[-1] - 1

# Load dataset
data = get_historical_data('SPY')

# Define parameter grid
param_grid = {
    'oversold': np.arange(20, 40),          # RSI 20-39
    'overbought': np.arange(60, 85),        # RSI 60-84
    'window': np.arange(5, 30),             # Window 5-29
    'trend_window': np.arange(50, 300, 10)  # MA 50-290
}

# Generate training data
param_samples = pd.DataFrame({
    'oversold': np.random.choice(param_grid['oversold'], 100),
    'overbought': np.random.choice(param_grid['overbought'], 100),
    'window': np.random.choice(param_grid['window'], 100),
    'trend_window': np.random.choice(param_grid['trend_window'], 100)
})

param_samples['return'] = param_samples.apply(lambda row: calculate_strategy_return(
    row['oversold'], row['overbought'], row['window'], row['trend_window'], data), axis=1)

# Prepare features and target
X = param_samples.drop(columns=['return'])
y = param_samples['return']

# Define Random Forest model
rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)

# Define a scorer function for maximizing returns
def return_scorer(y_true, y_pred):
    return np.mean(y_pred)  # Optimizing for highest predicted return

# Use make_scorer with the corrected function
custom_scorer = make_scorer(return_scorer, greater_is_better=True)


# Perform Randomized Search for best parameters
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions={
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    },
    n_iter=50,
    cv=TimeSeriesSplit(n_splits=5),
    scoring=custom_scorer
)

# Train the model
random_search.fit(X, y)

# Display best parameters
print("Best Random Forest parameters:", random_search.best_params_)
print(f"Best estimated return: {random_search.best_score_:.2%}")

# Train final model with best parameters
best_rf = random_search.best_estimator_
predicted_returns = best_rf.predict(X)

# Select best RSI parameters
best_index = np.argmax(predicted_returns)
best_params = X.iloc[best_index].to_dict()
print("Best RSI parameters:", best_params)

# Backtest using best parameters
best_strategy = RSIStrategy(**best_params)
signals = best_strategy.generate_rsi_signals(data)
results = best_strategy.calculate_returns(signals)

# Plot results
plt.figure(figsize=(12, 6))
(1 + results['strategy_returns']).cumprod().plot(label='Optimized Strategy')
(1 + results['daily_returns']).cumprod().plot(label='Buy & Hold')
plt.title(f"Best Parameters: {best_params}")
plt.legend()
plt.show()