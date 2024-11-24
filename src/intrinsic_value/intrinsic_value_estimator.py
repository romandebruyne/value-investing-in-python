import pandas as pd
import numpy as np
from src.utils.calculation_utils import CalculationUtils

class IntrinsicValueEstimator:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def apply_discounted_cash_flow_model(metric_series, current_shares, growth_rate, discount_rates,
                                         terminal_growth_rate, prediction_years):
        """Function to estimate a stock's intrinsic value (IV) via a Discounted Cash Flow Model."""

        # Check prediction_years input is valid:
        if (prediction_years < 1) or (prediction_years > 10):
            print("Invalid input for 'prediction_years'.")
            return np.nan

        # Define number of years for prediction period:
        last_year_in_dataset = int(metric_series.index[-1])

        # Create dictionary to collect intrinsic values for each discount rate
        discount_rate_to_intrinsic_value = {str(round(disc_rate * 100, 1)) + " %": 0 for disc_rate in discount_rates}

        # Loop for DCF calculations:
        for disc_rate in discount_rates:
            # Create list for predicted future values. First values is median value of used metric.
            median_metric = [np.nanmedian(metric_series)]

            if np.isnan(median_metric[0]):
                print("Median of used metric is NaN: return NaN.")
                return np.nan

            # Create list for discounted values:
            discounted_values = []

            for year in range(1, prediction_years + 1):
                median_metric.append(median_metric[-1] * (1 + growth_rate))
                discounted_values.append((median_metric[-1] / (1 + disc_rate) ** year))

            # Calculate Terminal Value (TV):
            terminal_value = IntrinsicValueEstimator.calculate_terminal_value(median_metric[0], disc_rate, growth_rate,
                                                                              terminal_growth_rate, prediction_years)

            # Company's Intrinsic Value = Sum of DCFs + Terminal Value
            intrinsic_value_company = np.sum(discounted_values[1:]) + terminal_value

            # Intrinsic value per Share
            intrinsic_value_per_share = intrinsic_value_company / current_shares

            # Add intrinsic value per share to dictionary:
            discount_rate_to_intrinsic_value[str(round(disc_rate * 100, 1)) + " %"] = intrinsic_value_per_share

        # Convert dictionary to pandas dataframe:
        return pd.DataFrame(discount_rate_to_intrinsic_value.values(),
                            index=discount_rate_to_intrinsic_value.keys(), columns=["IV_DCF"])

    @staticmethod
    def calculate_terminal_value(metric_value, discount_rate, growth_rate, terminal_growth_rate, prediction_years):
        """Function to calculate the Terminal Value."""
        term1_numerator = (metric_value * (1 + growth_rate) ** (prediction_years + 1) * (1 + terminal_growth_rate))
        term1_denominator = (discount_rate - terminal_growth_rate)
        term2 = (1 / (1 + discount_rate) ** (prediction_years + 1))
        return (term1_numerator / term1_denominator) * term2

    @staticmethod
    def apply_discounted_dividends_model(dividends_series, last_or_median, growth_rate, discount_rates,
                                         terminal_growth_rate, prediction_years):
        """Function to estimate intrinsic value (IV) via the Dividend Discount Model."""

        # Check prediction_years input is valid:
        if (prediction_years < 1) or (prediction_years > 10):
            print("Invalid input for 'prediction_years'.")
            return np.nan

        # Calculate median dividends and create list for projected future values:
        if last_or_median == "last":
            dividends_value = dividends_series[-1]
        elif last_or_median == "median":
            dividends_value = CalculationUtils.compute_median(dividends_series[-prediction_years:])
            if np.isnan(dividends_value):
                print("Median dividends are NaN. Return NaN.")
                return np.nan

        # Compute dividends in the next period (future projection):
        next_period_dividends = dividends_value * (1 + growth_rate)

        # Create dictionary to collect IV for each discount rate
        discount_rate_to_intrinsic_value = {str(round(disc_rate * 100, 1)) + " %": 0 for disc_rate in discount_rates}

        # Loop to estimate IVs with different discount rates:
        for disc_rate in discount_rates:
            intrinsic_value = next_period_dividends / (disc_rate - terminal_growth_rate)

            # Add intrinsic value per share to dictionary:
            discount_rate_to_intrinsic_value[str(round(disc_rate * 100, 1)) + " %"] = intrinsic_value

        # Convert dictionary to pandas dataframe:
        return pd.DataFrame(discount_rate_to_intrinsic_value.values(),
                            index=discount_rate_to_intrinsic_value.keys(), columns=["IV_DDM"])