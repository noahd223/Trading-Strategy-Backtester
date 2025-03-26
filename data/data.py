import yfinance as yf

def get_historical_data(ticker="SPY", start_date="2010-01-01", end_date="2023-01-01"):
    """Fetch historical price data from Yahoo Finance"""
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    # Ensure we only get the 'Close' column and rename it
    return df[['Close']].rename(columns={'Close': 'price'})

print(get_historical_data())