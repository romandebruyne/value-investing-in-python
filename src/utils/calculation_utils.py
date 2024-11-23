import pandas as pd
import numpy as np
from src.intrinsic_value.growth_rate_calculator import GrowthRateCalculator

class CalculationUtils:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def calculate_covariance_matrix(series_x, series_y):
        return np.cov(series_x, series_y)

    @staticmethod
    def compute_median(values):
        # If more than 50% of datapoints are NaN, return NaN:
        if pd.isna(values).sum() < len(values) * 0.5:
            return np.nanmedian(values)
        else:
            return np.nan

    @staticmethod
    def calculate_median_growth_rates(dataset):
        # Define growth rate metrics:
        relevant_metrics = ['revenue_mil', 'operating_income_mil', 'net_income_mil', 'eps', 'dividends', 'bvps',
                            'operating_cash_flow_mil', 'free_cash_flow_mil', 'capex_mil']

        # Define assessment periods (last period = 9, because only 9 growth rates for a 10 year period are available):
        assessment_periods = [9, 3, 1]

        # Create dictionary to collect metric name and corresponding values:
        results = {key: [] for key in relevant_metrics}

        for metric in relevant_metrics:
            # Create series containing the metric's values:
            if metric == "capex_mil":
                metric_series = dataset[metric] * (-1)
            else:
                metric_series = dataset[metric]

            for period in assessment_periods:
                # Compute compound annual growth rate (CAGR) & append median CAGR to dictionary:
                results[metric].append(GrowthRateCalculator.calculate_median_cagr(metric_series, period))

        # Return results as dataframe:
        return pd.DataFrame(results.values(), index=results.keys(), columns=['10Y', '3Y', '1Y'])

    @staticmethod
    def calculate_median_values(dataset):
        # Define growth rate metrics:
        relevant_metrics = ['payout_ratio', 'interest_coverage_ratio', 'operating_margin_pct', 'net_margin_pct',
                            'gross_margin_pct', 'return_on_equity_pct', 'return_on_assets_pct',
                            'return_on_invested_capital_pct', 'free_cash_flow_to_revenue', 'current_ratio',
                            'debt_to_equity_ratio']

        # Define assessment periods:
        assessment_periods = [10, 3, 1]

        # Create dictionary to collect metric name and corresponding values:
        results = {key: [] for key in relevant_metrics}

        for metric in relevant_metrics:
            # Create series containing the metric's values:
            metric_series = dataset[metric]

            for period in assessment_periods:
                # Append median value to dictionary:
                results[metric].append(CalculationUtils.compute_median(metric_series[-period:]))

        # Return results as dataframe:
        return pd.DataFrame(results.values(), index=results.keys(), columns=['10Y', '3Y', '1Y'])