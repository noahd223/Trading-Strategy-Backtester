import yfinance as yf

# change dates here to get different dates for the data
def get_historical_data(ticker="SPY", start_date="2015-01-01", end_date="2025-01-01"):
    """Fetch historical price data from Yahoo Finance"""
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    # Ensure we only get the 'Close' column and rename it
    return df[['Close']].rename(columns={'Close': 'price'})
