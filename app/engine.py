import pandas as pd
import numpy as np
import yfinance as yf

class PortfolioEngine:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.tickers = []
        self.weights = []
        self.port_data = None 
        
    def load_portfolio(self):
        """ Loads data from the CSV file specified by self.csv_path and populates self.tickers and self.weights.
            Raises:
                FileNotFoundError: If the CSV file cannot be found at the specified path.
                ValueError: If the CSV file does not contain the required columns or if the weights dont sum to 1
        """
        try:
            df = pd.read_csv(self.csv_path) 

            if 'Ticker' not in df.columns or 'Weight' not in df.columns:
                raise ValueError("CSV must contain 'Ticker' and 'Weight' columns.")
            
           
            total = df['Weight'].sum()
            
            if 90 < total < 110:
                df['Weight'] = df['Weight'] / 100.0
                total = df['Weight'].sum()

            if abs(total - 1.0) > 1e-4:
                raise ValueError(f"Weights must sum to 1.0, but they sum to {total}")
            
            self.tickers = df['Ticker'].tolist() 
            self.weights = df['Weight'].values
            self.port_data = df[['Ticker', 'Weight']] 

        except FileNotFoundError:
            raise FileNotFoundError(f"could not find file at {self.csv_path}")
        except Exception as e:
            raise ValueError(f"something wrong with program{e}")

    def get_price_history(self, period="1y"):
        """ Fetches the historical closing prices for tickers over a year with yfinance.
            Args:
                period (str): The time period for which to fetch historical default is "1y"
            Returns:
                prices_df: A DataFrame containing the historical closing prices for the tickers.
            Raises:
                ValueError: If there is an issue with fetching the price data.
        """
        
        data = yf.download(self.tickers, period=period, progress=False, threads=False)
        

        prices_df = pd.DataFrame()

        if 'Adj Close' in data.columns:
            temp_data = data['Adj Close']
            if not temp_data.dropna(how='all').empty:
                prices_df = temp_data

        if prices_df.empty and 'Close' in data.columns:
            prices_df = data['Close']
        
        if prices_df.empty:
            try:
                prices_df = data.xs('Adj Close', axis=1, level=0)
            except KeyError:
                pass

        if prices_df.empty:
            if not data.empty and len(data.columns) == len(self.tickers):
                prices_df = data
            else:
                raise ValueError(f"Failed to fetch price data. YF Returned: {data.columns}")

        return prices_df

    def calculate_volatility(self, prices_df):
        """Calculates volatility of given portfolio
            Args:
                prices_df: A DataFrame containing historical closing prices.
            Returns:
                volatility: The volatility of the portfolio 
            Raises:
                ValueError: if prices_df or returns is empty and if prices_df length is less than 2 
        """

        if prices_df.empty:
            raise ValueError("Prices_df is empty")
        if len(prices_df) < 2:
            raise ValueError("need 2 days of price data")
        
        # sanitation layer
        # check for bad tickers 
        prices_df = prices_df.dropna(axis=1, how='all')
        
        if prices_df.empty:
             raise ValueError("All tickers failed to download.")

        valid = prices_df.columns.tolist()

        weights = self.port_data['Weight'].tolist()
        s = pd.Series(weights, index=self.port_data['Ticker'].tolist())

       
        clean_tickers = [col[1] if isinstance(col, tuple) else col for col in valid]

        clean_tickers = [str(t).strip().upper() for t in clean_tickers]

        align = s[clean_tickers]
        
        if align.empty:
            raise ValueError(f"No weights found for tickers: {clean_tickers}")
        
        align = align / align.sum()
        
        prices_df = prices_df.ffill()
        returns = np.log(prices_df).diff().dropna() 

        if returns.empty:
            raise ValueError("no vaild returns data")
        
        cov_matrix = returns.cov()
        annual = cov_matrix * 252

        final_weights = align.values
        
        variance = np.dot(final_weights.T, np.dot(annual, final_weights))
        volatility = np.sqrt(variance)

        return volatility

if __name__ == "__main__":
    engine = PortfolioEngine("data/sample_portfolio.csv")
    engine.load_portfolio()
    prices = engine.get_price_history()
    risk = engine.calculate_volatility(prices)
    print(f"Portfolio Volatility: {risk:.2%}")