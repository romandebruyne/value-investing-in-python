import pandas as pd
import numpy as np
from src.utils.calculation_utils import CalculationUtils

class BetaEstimator:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def estimate_beta(stock_prices, benchmark_prices, period, data_frequency):
        """Function to estimate a beta factor based on stock and benchmark price data,
        The calculation can be done for different timeframes, e.g. 1-year beta factor."""

        if data_frequency.value not in ["daily", "monthly"]:
            print("Invalid data frequency.")
            return np.nan

        # Determine required datapoints:
        data_points_required = BetaEstimator.determine_required_datapoints(period, data_frequency)

        # Create subsets of stock/ benchmark data:
        if data_points_required > len(stock_prices) or data_points_required > len(benchmark_prices):
            print("Not enough data points!")
            return np.nan
        else:
            stock_subset = stock_prices.iloc[-data_points_required:]
            benchmark_subset = benchmark_prices.iloc[-data_points_required:]

        # Calculate returns & cumulative returns:
        stock_returns = BetaEstimator.calculate_cumulative_returns(stock_subset)
        benchmark_returns = BetaEstimator.calculate_cumulative_returns(benchmark_subset)

        # Estimate variance of benchmark & covariance between stock and benchmark returns:
        covariance_matrix = CalculationUtils.calculate_covariance_matrix(stock_returns['Cumulative_Returns'][1:],
                                                                         benchmark_returns['Cumulative_Returns'][1:])
        benchmark_variance = covariance_matrix[1, 1]
        covariance_stock_benchmark = covariance_matrix[0, 1]

        # Return estimated beta:
        return covariance_stock_benchmark / benchmark_variance

    @staticmethod
    def determine_required_datapoints(period, data_frequency):
        """Function to determine number of required data points (observations) to calculate returns.
        252 days = 1 trading year = 12 months"""

        if data_frequency.value == "daily":
            return (period.value * 252) + 1
        elif data_frequency.value == "monthly":
            return (period.value * 12) + 1
        else:
            return 9999

    @staticmethod
    def calculate_cumulative_returns(price_data):
        """Function calculate returns and cumulative returns."""

        # Calculate returns
        return_data = pd.DataFrame(data=price_data['Adj Close'].rename("Returns", inplace=True).pct_change(),
                                   index=price_data.index)

        # Calculate cumulative returns
        return_data['Cumulative_Returns'] = (1 + return_data['Returns']).cumprod()

        return return_data