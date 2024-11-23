import pandas as pd
import numpy as np
from src.utils.calculation_utils import CalculationUtils
from src.utils.company_region import CompanyRegion


class DiscountRateEstimator:
    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def estimate_discount_rate(morningstar_dataset, spreads_nonfinancials, spreads_financials, risk_premiums,
                      risk_free_rate, beta, company_type, company_region, period):
        """ Function to estimate weighted average capital cost (WACC), which serve as proxy for the discount rate."""

        # Compute median tax rate & interest coverage ratio.
        median_tax_rate = CalculationUtils.compute_median(morningstar_dataset["tax_rate_pct"][(-period.value):])
        median_interest_coverage_ratio = CalculationUtils.compute_median(
            morningstar_dataset["interest_coverage_ratio"][(-period.value):])

        # Check medians:
        if pd.isna(median_tax_rate) or pd.isna(median_interest_coverage_ratio):
            print("At least one input factors is NaN. Discount rate = NaN.")
            return np.nan

        # 1. Calculate Debt Cost:
        debt_cost_after_tax = DiscountRateEstimator.estimate_debt_cost_after_tax(company_type, spreads_nonfinancials,
                                                                                 spreads_financials,
                                                                                 median_tax_rate,
                                                                                 median_interest_coverage_ratio,
                                                                                 risk_free_rate)

        # 2. Calculate Equity Cost:
        equity_cost = DiscountRateEstimator.estimate_equity_cost(company_region, risk_premiums, risk_free_rate, beta)

        # 3. Determine capital structure:
        median_equity_ratio = CalculationUtils.compute_median(morningstar_dataset["equity_ratio_pct"]
                                                              [(-period.value):]) / 100

        if not np.isnan(median_equity_ratio):
            median_debt_ratio = 1 - median_equity_ratio
        else:
            median_equity_rate = np.nan
            median_debt_ratio = np.nan
            print("Equity ratio NaN. Return NaN.")
            return np.nan

        # Return WACC/ Discount Rate
        return (median_equity_ratio * equity_cost) + (median_debt_ratio * debt_cost_after_tax)

    @staticmethod
    def estimate_debt_cost_after_tax(company_type, spreads_nonfinancials, spreads_financials, median_tax_rate,
                                     median_interest_coverage_ratio, risk_free_rate):
        """Function to estimate debt cost after tax."""

        # Determine what spread data is used (depending on company type):
        if company_type.value == "nonfinancial":
            spreads = spreads_nonfinancials
        elif company_type.value == "financial":
            spreads = spreads_financials
        else:
            print("Invalid company type.")
            return np.nan

        # Determine spread according to table:
        for row in range(len(spreads)):
            upper_bound = spreads.iloc[row, 1]
            lower_bound = spreads.iloc[row, 0]
            if (median_interest_coverage_ratio > lower_bound) and (median_interest_coverage_ratio <= upper_bound):
                spread = spreads.iloc[row, 3]

        # Calculate debt cost before tax:
        debt_cost_before_tax = risk_free_rate + spread

        # Returning debt cost after tax:
        return debt_cost_before_tax * (1 - (median_tax_rate / 100))

    @staticmethod
    def estimate_equity_cost(company_region, risk_premiums, risk_free_rate, beta):
        """Function to estimate equity cost."""

        # Check company region input:
        if company_region not in [r for r in CompanyRegion]:
            print("Invalid company region.")
            return np.nan

        # Determine Risk Premium:
        risk_premium = risk_premiums[risk_premiums["region"] == company_region.value]["ERP"].item()

        # Return Equity Cost:
        return risk_free_rate + (risk_premium * beta)