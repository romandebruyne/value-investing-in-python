import numpy as np

class GrowthRateCalculator:
    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def calculate_median_cagr(metric_series, period):
        """Function to calculate the median compound annual growth rate (CAGR)"""
        from src.utils.calculation_utils import CalculationUtils

        # Create list containing years included in the period:
        years = [int(year) for year in list(metric_series.index)[-(period + 1):]]

        # Create empty list to collect growth rates:
        cagrs = []

        for year in years[:-1]:
            start_value = metric_series[str(year)]

            for forward_step in range(1, len(years), 1):
                end_value = metric_series[str(year + forward_step)]

                # If start or end values = 0, append NaN; otherwise compute compound annual growth rate (CAGR):
                if np.min([start_value, end_value]) <= 0:
                    cagrs.append(np.nan)
                    continue
                else:
                    cagr = (end_value / start_value) ** (1 / forward_step)
                    cagrs.append(cagr - 1)

            years.pop(-1)

        return CalculationUtils.compute_median(cagrs)

    @staticmethod
    def determine_optimal_growth_rate(metric_growth_rate, return_on_equity, benchmark_growth_rate=None):
        """Function to compare different growth rates and determine optimal one."""

        # Check input:
        if np.isnan(metric_growth_rate):
            print("Metric growth rate is NaN. Return NaN.")
            return np.nan

        # Print options:
        print(f"Metric growth rate: {round(metric_growth_rate * 100, 2)}%")
        if benchmark_growth_rate is not None:
            print(f"Benchmark growth rate: {round(benchmark_growth_rate * 100, 2)}%")
        print(f"Return on Equity: {round(return_on_equity * 100, 2)}%")
        print("")

        # String for printing decision:
        chosen_growth_rate = ""

        # Comparing the growth rates:
        if benchmark_growth_rate is not None:
            if metric_growth_rate > benchmark_growth_rate:
                optimal_growth_rate = benchmark_growth_rate
                chosen_growth_rate = "Benchmark CAGR"
            else:
                optimal_growth_rate = metric_growth_rate
                chosen_growth_rate = "Metric CAGR"
        else:
            optimal_growth_rate = metric_growth_rate
            chosen_growth_rate = "Metric CAGR"

        if optimal_growth_rate > return_on_equity:
            optimal_growth_rate = return_on_equity
            chosen_growth_rate = "RoE"

        if optimal_growth_rate < 0:
            optimal_growth_rate = 0
            chosen_growth_rate = "Zero growth"

        print(f'Optimal growth rate: {chosen_growth_rate}, {round(optimal_growth_rate * 100, 2)}%')
        return optimal_growth_rate