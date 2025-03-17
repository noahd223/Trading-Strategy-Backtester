from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Download historical data
def download_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)["Close"]
    return data

# Calculate strategy returns for a single stock
def moving_average_strategy(data, stock_ticker, short_window=50, long_window=200):
    df = pd.DataFrame({stock_ticker: data[stock_ticker]})
    
    # Calculate moving averages
    df['SMA50'] = df[stock_ticker].rolling(short_window).mean()
    df['SMA200'] = df[stock_ticker].rolling(long_window).mean()
    
    # Generate signals
    df['position'] = (df['SMA50'] > df['SMA200']).astype(int).shift(1).fillna(0)
    
    # Calculate returns
    df['daily_return'] = df[stock_ticker].pct_change()
    df['strategy_return'] = df['position'] * df['daily_return']
    df['cumulative_strategy'] = (1 + df['strategy_return']).cumprod()
    
    return df['cumulative_strategy']

# Calculate strategy returns for a basket of stocks
def basket_strategy(data, basket, short_window=50, long_window=200):
    results = pd.DataFrame()
    
    for stock in basket:
        stock_returns = moving_average_strategy(data, stock, short_window, long_window)
        results[stock] = stock_returns
    
    # Calculate equal-weighted portfolio returns
    results['Basket'] = results.mean(axis=1)
    return results

# Calculate S&P 500 returns
def calculate_sp500_returns(data):
    sp500 = pd.DataFrame({'S&P500': data['SPY']})
    sp500['daily_return'] = sp500['S&P500'].pct_change()
    sp500['cumulative_sp500'] = (1 + sp500['daily_return']).cumprod()
    return sp500['cumulative_sp500']

# Plot results using Plotly
def plot_results(basket_results, sp500_returns):
    combined = pd.DataFrame({
        'Basket Strategy': basket_results['Basket'],
        'S&P 500': sp500_returns
    }).dropna()
    
    # Create interactive plot
    fig = go.Figure()
    
    # Add Basket Strategy line
    fig.add_trace(go.Scatter(
        x=combined.index,
        y=combined['Basket Strategy'],
        name='Basket Strategy',
        line=dict(color='#1F77B4', width=3),
        hovertemplate='Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
    ))
    
    # Add S&P 500 line
    fig.add_trace(go.Scatter(
        x=combined.index,
        y=combined['S&P 500'],
        name='S&P 500',
        line=dict(color='#FF7F0E', width=3, dash='dot'),
        hovertemplate='Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title='Basket Strategy vs. S&P 500 Performance',
        xaxis_title='Date',
        yaxis_title='Growth of $1 Investment',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        height=600,
        width=1000
    )
    
    # Add annotations
    fig.add_annotation(
        x=combined.index[-1],
        y=combined['Basket Strategy'].iloc[-1],
        text=f"Basket: ${combined['Basket Strategy'].iloc[-1]:.2f}",
        showarrow=True,
        arrowhead=1,
        ax=-50,
        ay=-40
    )
    
    fig.add_annotation(
        x=combined.index[-1],
        y=combined['S&P 500'].iloc[-1],
        text=f"S&P 500: ${combined['S&P 500'].iloc[-1]:.2f}",
        showarrow=True,
        arrowhead=1,
        ax=-50,
        ay=40
    )
    
    # Show plot
    fig.show()

# Main execution
if __name__ == "__main__":
    # Define basket of stocks and benchmark
    # TODO: Dynamically change basket
    basket = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # Example basket
    benchmark = ['SPY']  # S&P 500 proxy
    tickers = basket + benchmark
    
   

    #Define date range
    end_date = datetime.today()  # Today's date
    start_date = datetime.today() - timedelta(days=30*365)  # 30 years ago
    
    # Download data
    data = download_data(tickers, start_date, end_date)
    
    # Calculate basket strategy returns
    basket_results = basket_strategy(data, basket)
    
    # Calculate S&P 500 returns
    sp500_returns = calculate_sp500_returns(data)
    
    # Plot results
    plot_results(basket_results, sp500_returns)