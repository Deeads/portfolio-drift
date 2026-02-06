import pandas as pd
import numpy as np
import yfinance as yf

class PortfolioEngine:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.tickers = []
        self.weights = []
        
    def load_portfolio(self):
        """
        Task 1: Load the CSV.
        1. Read the CSV at self.csv_path
        2. Validate that the 'Weight' column sums to 1.0 (allow for small float error like 0.9999)
        3. If it doesn't sum to 1, raise a ValueError.
        4. Save tickers to self.tickers and weights to self.weights
        """
        # TODO: WRITE YOUR CODE HERE
        try:
            df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"could not find file at {self.csv_path}")
        except Exception as e:
            raise ValueError(f"something wrong with program{e}")
    def get_price_history(self, period="1y"):
        """
        Task 2: Get data from yfinance.
        1. Use yfinance to download 'Adj Close' for self.tickers.
        2. Return the DataFrame.
        """
        # TODO: WRITE YOUR CODE HERE
        pass

    def calculate_volatility(self, prices_df):
        """
        Task 3: The Hard Math.
        This is the most important interview question.
        
        Logic:
        1. Calculate daily returns (percent change) from prices_df.
        2. Calculate the Covariance Matrix of those returns.
        3. Annualize the Covariance (multiply by 252 trading days).
        4. Calculate Portfolio Variance using the Dot Product formula:
           variance = weights_transpose @ covariance_matrix @ weights
        5. Take the square root of variance to get Volatility (Standard Deviation).
        """
        # TODO: WRITE YOUR CODE HERE
        # Hint: Use np.dot() for matrix multiplication
        # Hint: weights needs to be a numpy array, not a list
        pass

if __name__ == "__main__":
    # Test your code here
    engine = PortfolioEngine("data/sample_portfolio.csv")
    engine.load_portfolio()
    prices = engine.get_price_history()
    risk = engine.calculate_volatility(prices)
    print(f"Portfolio Volatility: {risk:.2%}")