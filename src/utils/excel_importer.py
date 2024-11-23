import os
import pandas as pd
import numpy as np
from src.utils.data_category import DataCategory

class ExcelImporter:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def import_xls_file(file_name, category, columns_to_remove):
        """Read .xls file and return data as a pandas dataframe."""
        file_path = os.path.join("../data/", file_name)

        if category.value == 'growth':
            df = pd.read_excel(file_path, header=0)
            df.drop(df.index[[0, 2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19]], inplace=True)
            df.set_index(pd.Series(['revenue_growth', 'operating_income_growth', 'net_income_growth', 'eps_growth']),
                         inplace=True)
            df.drop(axis=1, columns=[df.columns[0], 'Latest Qtr'], inplace=True)
        else:
            df = pd.read_excel(file_path, header=0, index_col=0)
            df.rename_axis(None, inplace=True)
            df.drop(axis=1, columns=columns_to_remove, inplace=True)
            df = ExcelImporter.rename_indexes(df, category)

        df = ExcelImporter.remove_missing_datapoints(df)
        df.columns = ExcelImporter.get_relevant_years(int(list(df.columns)[-1][:4]))
        return df.astype('float64')

    @staticmethod
    def import_all_xls_files(file_names):
        """Read all .xls file and return data as a pandas dataframe."""
        dataframes = []

        for file_name in file_names:
            if 'growth' in file_name:
                dataframes.append(ExcelImporter.import_xls_file(file_name, DataCategory.GROWTH, []))
            elif 'operating' in file_name:
                dataframes.append(ExcelImporter.import_xls_file(file_name, DataCategory.OPERATING,
                                                                   ['Current', '5-Yr']))
            elif 'financial' in file_name:
                dataframes.append(ExcelImporter.import_xls_file(file_name, DataCategory.FINANCIAL_HEALTH,
                                                       ['Latest Qtr']))
            elif 'cash' in file_name:
                dataframes.append(ExcelImporter.import_xls_file(file_name, DataCategory.CASH_FLOW, ['TTM']))
            elif 'dividends' in file_name:
                dataframes.append(ExcelImporter.import_xls_file(file_name, DataCategory.DIVIDENDS, []))

        combined_df = pd.concat(dataframes)
        return combined_df

    @staticmethod
    def get_relevant_years(end_year):
        """Create list including 10 years and return it."""
        return [year for year in range(end_year + 1 - 10, end_year + 1, 1)]

    @staticmethod
    def remove_missing_datapoints(df):
        """Remove missing data points from pandas dataframe and return dataframe."""
        with pd.option_context('future.no_silent_downcasting', True):
            df.replace(to_replace='-', value=np.nan, inplace=True)
            df.dropna(axis=0, how='all', inplace=True)
        return df

    @staticmethod
    def rename_indexes(dataset, data_category):
        """Rename indexes of pandas dataframe and return the dataframe."""
        if data_category.value == 'operating and efficiency':
            index_to_new_index = {
                'Gross Margin %': 'gross_margin_pct',
                'Operating Margin %': 'operating_margin_pct',
                'Net Margin %': 'net_margin_pct',
                'EBITDA Margin %': 'ebitda_margin_pct',
                'Tax Rate %': 'tax_rate_pct',
                'Return on Asset %': 'return_on_assets_pct',
                'Return on Equity %': 'return_on_equity_pct',
                'Return on Invested Capital %': 'return_on_invested_capital_pct',
                'Interest Coverage': 'interest_coverage_ratio',
                'Days Sales Outstanding': 'days_sales_outstanding',
                'Days Inventory': 'days_inventory',
                'Payables Period': 'payables_period',
                'Cash Conversion Cycle': 'cash_conversion_cycle',
                'Recieveables Turnover': 'receivables_turnover',
                'Inventory Turnover': 'inventory_turnover',
                'Fixed Assets Turnover': 'fixed_asset_turnover',
                'Asset Turnover': 'asset_turnover',
            }
        elif data_category.value == 'financial health':
            index_to_new_index = {
                'Current Ratio': 'current_ratio',
                'Quick Ratio': 'quick_ratio',
                'Financial Leverage': 'financial_leverage',
                'Equity Ratio': 'equity_ratio_pct',
                'Debt/Equity': 'debt_to_equity_ratio',
                'Book Value/Share': 'bvps'
            }
        elif data_category.value == 'cash flow':
            index_to_new_index = {
                'Operating Cash Flow Growth % YOY': 'operating_cash_flow_growth',
                'Free Cash Flow Growth % YOY': 'free_cash_flow_growth',
                'Cap Ex as a % of Sales': 'capex_as_pct_of_sales',
                'Free Cash Flow/Sales %': 'free_cash_flow_to_revenue',
                'Free Cash Flow/Net Income': 'free_cash_flow_to_net_income',
                'Free Cash Flow/Share': 'free_cash_flow_to_shares'
            }
        else:
            return dataset

        dataset.rename(index=index_to_new_index, inplace=True)
        return dataset

    @staticmethod
    def import_spread_tables_excel(file_name):
        file_path = os.path.join("../data/", file_name)
        return pd.read_excel(file_path, sheet_name=0, header=0, skiprows=17, nrows=15, usecols='A:D,F:I')

    @staticmethod
    def import_risk_premiums_excel(file_name):
        file_path = os.path.join("../data/", file_name)
        return pd.read_excel(file_path, sheet_name='Regional Weighted Averages', header=0, skiprows=182, nrows=11,
                             usecols='A:B')