import pandas as pd
from src.utils.excel_importer import ExcelImporter

class DatabaseUtils:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def calculate_historical_values_via_growth_rates(base_value, growth_rates_series):
        historical_values = [base_value]

        for gr in growth_rates_series[::-1]:
            historical_value = historical_values[-1] / (1 + (gr / 100.0))
            historical_values.append(historical_value)
        historical_values = list(reversed(historical_values[:-1]))

        return historical_values

    @staticmethod
    def add_calculated_historical_values_to_dataset(metric_to_base_value, dataset):
        for key, val in metric_to_base_value.items():
            historical_values = DatabaseUtils.calculate_historical_values_via_growth_rates(val,
                                                                                           dataset.loc[key + '_growth'])
            historical_values_df = pd.DataFrame(historical_values, columns=[key + '_mil' if key != 'eps' else key],
                                                index=dataset.columns)
            dataset = pd.concat([dataset, historical_values_df.T], axis=0)

        return dataset

    @staticmethod
    def estimate_historical_capex_values(revenue_series, capex_as_pct_of_sales_series):
        zipped_list = list(zip(list(revenue_series), list(capex_as_pct_of_sales_series)))
        return [-(rev * capex_sales / 100.0) for (rev, capex_sales) in zipped_list]

    @staticmethod
    def estimate_historical_shares_values(free_cf_series, free_cf_to_shares_series):
        zipped_list = list(zip(list(free_cf_series), list(free_cf_to_shares_series)))
        return [free_cf / fcf_to_shares for (free_cf, fcf_to_shares) in zipped_list]

    @staticmethod
    def estimate_historical_total_equity_values(book_values_per_share_series, shares_series):
        zipped_list = list(zip(list(book_values_per_share_series), list(shares_series)))
        return [bvps * shares for (bvps, shares) in zipped_list]

    @staticmethod
    def estimate_historical_total_assets_values(return_on_assets_series, net_income_series):
        zipped_list = list(zip(list(return_on_assets_series), list(net_income_series)))
        return [net_income / (roa / 100.0) for (roa, net_income) in zipped_list]

    @staticmethod
    def estimate_historical_equity_ratio_values(book_values_per_share_series, shares_series, return_on_assets_series,
                                                net_income_series):
        # First: estimation of total equity
        total_equity = DatabaseUtils.estimate_historical_total_equity_values(book_values_per_share_series,
                                                                             shares_series)

        # Second: estimation of total assets
        total_assets = DatabaseUtils.estimate_historical_total_assets_values(return_on_assets_series, net_income_series)

        # Third: divide total equity by total assets to determine equity ratio
        return [(equity / assets) * 100.0 for (equity, assets) in list(zip(total_equity, total_assets))]

    @staticmethod
    def add_estimated_historical_values_to_dataset(dataset):
        estimated_capex_list = DatabaseUtils.estimate_historical_capex_values(dataset.loc['revenue_mil'],
                                                                              dataset.loc['capex_as_pct_of_sales'])
        estimated_capex_df = pd.DataFrame(estimated_capex_list, columns=['capex_mil'], index=dataset.columns)
        dataset = pd.concat([dataset, estimated_capex_df.T])

        estimated_shares_list = DatabaseUtils.estimate_historical_shares_values(dataset.loc['free_cash_flow_mil'],
                                                                                dataset.loc['free_cash_flow_to_shares'])
        estimated_shares_df = pd.DataFrame(estimated_shares_list, columns=['shares_mil'], index=dataset.columns)
        dataset = pd.concat([dataset, estimated_shares_df.T])

        estimated_equity_ratios_list = DatabaseUtils.estimate_historical_equity_ratio_values(dataset.loc['bvps'],
                                                                                             dataset.loc['shares_mil'],
                                                                                             dataset.loc['return_on_assets_pct'],
                                                                                             dataset.loc['net_income_mil'])
        estimated_equity_ratios_df = pd.DataFrame(estimated_equity_ratios_list, columns=['equity_ratio_pct'],
                                                  index=dataset.columns)
        dataset = pd.concat([dataset, estimated_equity_ratios_df.T])

        return dataset

    @staticmethod
    def create_complete_dataset(paths, metric_to_base_values):
        dataset = ExcelImporter.import_all_xls_files(paths)
        dataset = DatabaseUtils.add_calculated_historical_values_to_dataset(metric_to_base_values, dataset)
        dataset = DatabaseUtils.add_estimated_historical_values_to_dataset(dataset)
        return dataset

    @staticmethod
    def reduce_dataset(dataset):
        columns_to_keep = ['shares_mil', 'revenue_mil', 'operating_income_mil', 'net_income_mil', 'eps', 'dividends',
                           'payout_ratio', 'bvps', 'operating_margin_pct', 'net_margin_pct', 'gross_margin_pct',
                           'interest_coverage_ratio', 'tax_rate_pct', 'return_on_assets_pct', 'return_on_equity_pct',
                           'return_on_invested_capital_pct', 'operating_cash_flow_mil', 'free_cash_flow_mil',
                           'free_cash_flow_to_revenue', 'capex_mil', 'current_ratio', 'debt_to_equity_ratio',
                           'equity_ratio_pct', 'asset_turnover']
        return dataset.loc[columns_to_keep]

    @staticmethod
    def transpose_dataset(dataset):
        return dataset.T.astype('float64')