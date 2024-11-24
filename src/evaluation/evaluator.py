import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from src.beta.beta_estimator import BetaEstimator
from src.utils.calculation_utils import CalculationUtils
from src.utils.period import Period
from src.utils.data_frequency import DataFrequency

class Evaluator:
    def __init__(self):
        raise NotImplementedError('This class should not be instantiated.')

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
        median_values['points'] = points_median_value

        return median_growth_rates, median_values

    @staticmethod
    def assess_intrinsic_value(stock_prices, intrinsic_value, margin_of_safety_pct):
        """"Function to check whether the stock is under- or overvalued."""

        # Get latest stock adjusted closing price:
        latest_adj_close = round(stock_prices['Adj Close'].iloc[-1], 2)
        print(f'Latest adjusted close price: {latest_adj_close}')
        print('')

        # Subtract the margin of safety (MoS) from intrinsic value:
        intrinsic_value_minus_margin = round(intrinsic_value * (1 - margin_of_safety_pct), 2)
        print(f'Intrinsic value (after Margin of Safety): {intrinsic_value_minus_margin}')
        print('')

        # Is stock under- or overvalued?
        if latest_adj_close > intrinsic_value_minus_margin:
            difference = latest_adj_close - intrinsic_value_minus_margin
            print(f'Stock is overvalued! Difference is equal to: {difference}')
        elif latest_adj_close < intrinsic_value_minus_margin:
            difference = intrinsic_value_minus_margin - latest_adj_close
            print(f'Stock is undervalued! Difference is equal to: {difference}')
        else:
            print('Indifference.')

        # Plot 1-year development
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.plot(stock_prices['Adj Close'])
        ax.set_title("Stock's adjusted closing prices over the last year")
        ax.axhline(intrinsic_value_minus_margin, color='red', label='Intrinsic Value (after Margin of Safety)')
        ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))
        ax.legend(loc='upper left')
        plt.show()

    @staticmethod
    def get_hrlr_score(stock_prices, benchmark_prices, latest_dividends):
        """Stock valuation according to 'High Returns from Low Risk' by Pim van Vliet & Jan de Koning.
        Function to compute/get the three key decision parameters: 1-Year Beta, Momentum, 1-Year Dividend Yield.
        The author's recommended values are as follows: 1-Year Beta: less than 1; Momentum: any positive value;
        1-Year Dividend Yield: higher or equal to 3."""

        # 1. 1-Year Beta:
        beta_one_year = BetaEstimator.estimate_beta(stock_prices, benchmark_prices, Period.ONE_YEAR,
                                                    DataFrequency.DAILY)

        # 2. Momentum (current price relative to price 252 days, i.e. 1 trading year, ago)
        momentum = (stock_prices['Adj Close'].iloc[-1] / stock_prices['Adj Close'].iloc[-252]) - 1

        # 3. 1-Year Dividend Yield:
        dividend_yield = latest_dividends / stock_prices['Adj Close'].iloc[-1]

        # Calculate stock's score:
        score = 0

        if beta_one_year < 1.0:
            score += 1
        if momentum > 0.0:
            score += 1
        if dividend_yield >= 3.0:
            score += 1

        # Print the results
        print(f'1-Year Beta: {round(beta_one_year, 2)}')
        print(f'Momentum: {round(momentum * 100, 2)}%')
        print(f'1-Year Dividend Yield: {round(dividend_yield * 100, 2)}%')
        print(f'Overall score: {score}/3')
        return score

    @staticmethod
    def get_piotroski_f_score(morningstar_dataset):
        """
        Function to determine the Piotroski F-Score (https://en.wikipedia.org/wiki/Piotroski_F-score).
        To determine the Piotroski F-Score the assessment of 9 criteria is conducted. For each criterion 1 or 0 points
        are possible. In the following, the criteria and the respective conditions to acquire 1 point are listed:
        1. Net Income: 1 point, if positive (greater than Zero)
        2. Operating Cash Flow: 1 point, if positive (greater than Zero)
        3. Operating Cash Flow vs. Net Income: 1 point, if operating cash flow is higher.
        4. Return on Assets: 1 point, if value increased (comparison of current and previous period)
        5. Debt-to-Equity: 1 point, if value decreased (comparison of current and previous period)
        6. Current Ratio: 1 point, if value increased (comparison of current and previous period)
        7. Shares Outstanding: 1 point, if value is constant or decreased (comparison of current and previous period)
        8. Gross Margin: 1 point, if value increased (comparison of current and previous period)
        9. Asset Turnover: 1 point, if value increased (comparison of current and previous period)
        """

        # List to collect points
        points = [0 for num in range(0, 10, 1)]

        # Get all the relevant metrics and corresponding values:
        net_income = morningstar_dataset['net_income_mil'].iloc[-1]
        operating_cash_flow = morningstar_dataset['operating_cash_flow_mil'].iloc[-1]

        if net_income > 0:
            points[0] = 1

        if operating_cash_flow > 0:
            points[1] = 1

        if operating_cash_flow > net_income:
            points[2] = 1

        if (round(morningstar_dataset['return_on_assets_pct'].iloc[-1], 1) >
                round(morningstar_dataset['return_on_assets_pct'].iloc[-2], 1)):
            points[3] = 1

        if (round(morningstar_dataset['debt_to_equity_ratio'].iloc[-1], 1) <
                round(morningstar_dataset['debt_to_equity_ratio'].iloc[-2], 1)):
            points[4] = 1

        if (round(morningstar_dataset['current_ratio'].iloc[-1], 1) >
                round(morningstar_dataset['current_ratio'].iloc[-2], 1)):
            points[5] = 1

        if (round(morningstar_dataset['shares_mil'].iloc[-1], 0) <=
                round(morningstar_dataset['shares_mil'].iloc[-2], 0)):
            points[6] = 1

        if (round(morningstar_dataset['gross_margin_pct'].iloc[-1], 1) >
                round(morningstar_dataset['gross_margin_pct'].iloc[-2], 1)):
            points[7] = 1

        if (round(morningstar_dataset['asset_turnover'].iloc[-1], 1) >
                round(morningstar_dataset['asset_turnover'].iloc[-2], 1)):
            points[8] = 1

        points[9] = sum(points)

        # Create Pandas DataFrame to inspect the results:
        criteria = ['Net Income', 'Operating Cash Flow', 'Op. Cash Flow vs. Net Income', 'Return on Assets',
                    'Debt/Equity', 'Current Ratio', 'Shares Outstanding', 'Gross Margin', 'Asset Turnover', 'F-Score']
        points_df = pd.DataFrame(points, index=criteria, columns=['Points'])

        # Print overall score:
        print(f'Piotroski F-Score: {sum(points) - points[9]}/9')

        return points_df