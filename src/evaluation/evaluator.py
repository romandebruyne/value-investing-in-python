import numpy as np
from src.utils.calculation_utils import CalculationUtils

class Evaluator:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def assess_metrics(dataset):
        median_growth_rates = CalculationUtils.calculate_median_growth_rates(dataset)
        median_values = CalculationUtils.calculate_median_values(dataset)

        # Growth rate metrics: 1 point, if positive (>0). Maximum points: 3.
        median_growth_rates['points'] = median_growth_rates.apply(lambda row: np.sum(row > 0), axis=1)

        # Median value metrics
        points_median_value = []

        # Payout ratio: 1, if value < 80%. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['payout_ratio', :] < 80))

        # Interest Coverage Ratio: 1, if value > 1.5. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['interest_coverage_ratio', :] > 1.5))

        # Operating margin, net margin, gross margin: 1, if value > 10%. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['operating_margin_pct', :] > 10))
        points_median_value.append(np.sum(median_values.loc['net_margin_pct', :] > 10))
        points_median_value.append(np.sum(median_values.loc['gross_margin_pct', :] > 10))

        # Return on Equity: 1, if value > 8%. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['return_on_equity_pct', :] > 8))

        # Return on Assets: 1, if value > 6%. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['return_on_assets_pct', :] > 8))

        # Return on Invested Capital: 1, if value > 8%. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['return_on_invested_capital_pct', :] > 8))

        # Free Cashflow to Revenue: 1, if value > 5%. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['free_cash_flow_to_revenue', :] > 5))

        # Current Ratio: 1, if value > 1. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['current_ratio', :] > 1))

        # Debt/Equity Ratio: 1, if value < 1. Maximum points: 3.
        points_median_value.append(np.sum(median_values.loc['debt_to_equity_ratio', :] < 1))

        # Assign the points to the dataframe:
        median_values["points"] = points_median_value

        return median_growth_rates, median_values