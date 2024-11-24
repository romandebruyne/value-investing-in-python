import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
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

    @staticmethod
    def assess_intrinsic_value(stock_prices, intrinsic_value, margin_of_safety_pct):
        """Function to check whether the stock is under- or overvalued."""

        # Get latest stock adjusted closing price:
        latest_adj_close = round(stock_prices['Adj Close'].iloc[-1], 2)
        print(f"Latest adjusted close price: {latest_adj_close}")
        print("")

        # Subtract the margin of safety (MoS) from intrinsic value:
        intrinsic_value_minus_margin = round(intrinsic_value * (1 - margin_of_safety_pct), 2)
        print(f"Intrinsic value (after Margin of Safety): {intrinsic_value_minus_margin}")
        print("")

        # Is stock under- or overvalued?
        if latest_adj_close > intrinsic_value_minus_margin:
            difference = latest_adj_close - intrinsic_value_minus_margin
            print(f"Stock is overvalued! Difference is equal to: {difference}")
        elif latest_adj_close < intrinsic_value_minus_margin:
            difference = intrinsic_value_minus_margin - latest_adj_close
            print(f"Stock is undervalued! Difference is equal to: {difference}")
        else:
            print("Indifference.")

        # Plot 1-year development
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.plot(stock_prices['Adj Close'])
        ax.set_title("Stock's adjusted closing prices over the last year")
        ax.axhline(intrinsic_value_minus_margin, color='red', label='Intrinsic Value (after Margin of Safety)')
        ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))
        ax.legend(loc="upper left")
        plt.show()