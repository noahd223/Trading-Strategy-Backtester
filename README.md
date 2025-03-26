# ML Trading Optimizer

This project focuses on optimizing financial trading strategies using machine learning techniques. It serves as a learning platform to explore the integration of machine learning models with common trading strategies to enhance their performance.

## Project Structure

The repository is organized as follows:

- `data/`: Contains modules for data retrieval and preprocessing.
- `strategies/`: Implements various trading strategies.
- `models/`: Includes machine learning models for optimizing trading strategies.
- `backtester.py`: A script to evaluate the performance of trading strategies using historical data.

## Installation

To set up the project environment, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/noahd223/ml-trading-optimizer.git
   ```

2. **Navigate to the project directory**:

   ```bash
   cd ml-trading-optimizer
   ```

3. **Install the required packages**:

   Ensure you have Python installed, then install the necessary packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

   If `requirements.txt` is not provided, manually install the packages as used in the project scripts, such as `numpy`, `pandas`, `matplotlib`, `scikit-learn`, etc.

## Usage

1. **Data Retrieval**:

   Use the `get_historical_data` function from the `data` module to fetch historical market data for a specific ticker symbol. For example:

   ```python
   from data.data import get_historical_data

   data = get_historical_data('SPY')
   ```

2. **Strategy Implementation**:

   Implement trading strategies using the classes provided in the `strategies` module. For instance, to use the RSI (Relative Strength Index) strategy:

   ```python
   from strategies.rsi import RSIStrategy

   strategy = RSIStrategy(oversold=30, overbought=70, window=14, trend_window=200)
   signals = strategy.generate_rsi_signals(data)
   ```

3. **Model Training and Optimization**:

   Train machine learning models to optimize the trading strategies. The `models` directory contains scripts that utilize models like `RandomForestRegressor` for this purpose. For example:

   ```python
   from models.rsi_model import train_rsi_model

   best_params = train_rsi_model(data)
   ```

4. **Backtesting**:

   Evaluate the performance of the trading strategy using the `backtester.py` script:

   ```bash
   python backtester.py
   ```

   This will output performance metrics and visualizations comparing the strategy's returns against a benchmark.

## Contributing

Contributions to enhance the functionality or add new features are welcome. Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with descriptive messages.
4. Push your changes to your fork.
5. Submit a pull request to the main repository.

*Note: This project is intended for educational purposes to explore the application of machine learning in trading strategies. It is not intended for live trading or financial advice.* 
