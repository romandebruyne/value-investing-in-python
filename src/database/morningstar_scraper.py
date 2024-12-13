import pandas as pd
import numpy as np
import requests
import time

from src.utils.data_category import DataCategory
from src.utils.database_utils import DatabaseUtils

class MorningstarScraper:
    def __init__(self, base_url, headers=None):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def define_url(morningstar_stock_identifier, data_category):
        base_url = 'https://api-global.morningstar.com/sal-service/v1/stock/'

        urls_dict = {
            'growth': '{}/keyStats/growthTable/{}'.format(base_url, morningstar_stock_identifier),
            'operating and efficiency': '{}/keyStats/OperatingAndEfficiency/{}'.format(base_url,
                                                                                       morningstar_stock_identifier),
            'financial health': '{}/keyStats/financialHealth/{}'.format(base_url, morningstar_stock_identifier),
            'cash flow': '{}/keyStats/cashFlow/{}'.format(base_url, morningstar_stock_identifier),
            'dividends': '{}/dividends/v4/{}/data'.format(base_url, morningstar_stock_identifier),
            'financials': '{}/newfinancials/{}/annual/summary'.format(base_url, morningstar_stock_identifier)
        }

        return urls_dict[data_category]

    @staticmethod
    def define_request_header():
        return {
            'apikey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          + 'Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0'
        }

    @staticmethod
    def define_payload_components():
        return {
            'growth': 'sal-components-key-stats-growth-table',
            'operating and efficiency': 'sal-components-key-stats-oper-efficiency',
            'financial health': 'sal-components-key-stats-financial-health',
            'cash flow': 'sal-components-key-stats-cash-flow',
            'dividends': 'sal-components-dividends',
            'financials': 'sal-components-equity-financials-summary'
        }

    @staticmethod
    def define_payload(data_category, payload_components):
        if data_category.value == 'financials':
            return {
                'reportType': 'A',
                'languageId': 'en',
                'locale': 'en',
                'clientId': 'MDC',
                'component': payload_components[data_category.value],
                'version': '3.71.0'
            }
        else:
            return {
                'languageId': 'en',
                'locale': 'en',
                'clientId': 'MDC',
                'component': payload_components[data_category.value],
                'version': '3.71.0'
            }

    @staticmethod
    def scrape_morningstar_stock_identifier(stock_ticker, exchange_ticker):
        # Get Morningstar 'identifier' for stock
        base_url = 'https://www.morningstar.com/stocks'
        url = '{}/{}/{}/valuation'.format(base_url, exchange_ticker, stock_ticker)

        # Open webpage session
        with requests.Session() as sess:
            sess.headers.update(MorningstarScraper.define_request_header())
            response = sess.get(url)
            index_for_extraction = response.text.find('paragraph')
            identifier = response.text[index_for_extraction - 13:index_for_extraction - 3]

        return identifier

    @staticmethod
    def scrape_morningstar_data_subset(morningstar_stock_identifier, data_category):
        # Scrape subset of data from Morningstar (data on specified data category, e.g. cash flow)
        if morningstar_stock_identifier == "":
            print("Provided Morningstar stock identifier is empty. Return None.")
            return None

        ## Get URL
        url = MorningstarScraper.define_url(morningstar_stock_identifier, data_category.value)

        ## Get payload component and define payload
        payload_component = MorningstarScraper.define_payload_components()
        payload = MorningstarScraper.define_payload(data_category, payload_component)

        # Open webpage session
        with requests.Session() as sess:
            sess.headers.update(MorningstarScraper.define_request_header())
            response = sess.get(url, params=payload)
            data = response.json()

        return data

    @staticmethod
    def scrape_morningstar_data(morningstar_stock_identifier, time_out_for_requests):
        data = []
        all_data_categories = [e for e in DataCategory]

        if time_out_for_requests <= 0:
            time_out_for_requests = 20.0

        for category in all_data_categories:
            data.append(MorningstarScraper.scrape_morningstar_data_subset(morningstar_stock_identifier, category))
            time.sleep(time_out_for_requests)

        return data

    @staticmethod
    def collect_growth_data(json_container):
        growth_dict = {'names': ['revenue_growth', 'operating_income_growth', 'net_income_growth', 'eps_growth']}

        for item in json_container["dataList"][:-1]:
            year = item["fiscalPeriodYearMonth"][:4]
            growth_dict[year] = [item['revenuePer']['yearOverYear'], item['operatingIncome']['yearOverYear'],
                                 item['netIncomePer']['yearOverYear'], item['epsPer']['yearOverYear']]

        return pd.DataFrame(growth_dict, index=growth_dict['names']).drop(['names'], axis=1)

    @staticmethod
    def collect_efficiency_data(json_container):
        efficiency_dict = {'names': ['gross_margin_pct', 'operating_margin_pct', 'net_margin_pct', 'tax_rate_pct',
                                     'return_on_assets_pct', 'return_on_equity_pct', 'return_on_invested_capital_pct',
                                     'interest_coverage_ratio', 'asset_turnover']}

        for item in json_container["dataList"][:-3]:
            year = item["fiscalPeriodYear"]
            efficiency_dict[year] = [item['grossMargin'], item['operatingMargin'], item['netMargin'], item['taxRate'],
                                     item['roa'], item['roe'], item['roic'], item['interestCoverage'],
                                     item['assetsTurnover']]

        return pd.DataFrame(efficiency_dict, index=efficiency_dict['names']).drop(['names'], axis=1)

    @staticmethod
    def collect_financial_health_data(json_container):
        financial_health_dict = {'names': ['current_ratio', 'debt_to_equity_ratio', 'bvps']}

        for item in json_container["dataList"][:-1]:
            year = item["fiscalPeriodYearMonth"][:4]
            financial_health_dict[year] = [item['currentRatio'], item['debtEquityRatio'], item['bookValuePerShare']]

        return pd.DataFrame(financial_health_dict, index=financial_health_dict['names']).drop(['names'], axis=1)

    @staticmethod
    def collect_cash_flow_data(json_container):
        cash_flow_dict = {'names': ['operating_cash_flow_growth', 'free_cash_flow_growth', 'free_cash_flow_to_revenue',
                                   'free_cash_flow_to_shares', 'capex_as_pct_of_sales']}

        for item in json_container["dataList"][:-1]:
            year = item["fiscalPeriodYearMonth"][:4]
            cash_flow_dict[year] = [item['operatingCFGrowthPer'], item['freeCashFlowGrowthPer'], item['freeCFPerSales'],
                                   item['freeCashFlowPerShare'], item['capExAsPerOfSales']]

        return pd.DataFrame(cash_flow_dict, index=cash_flow_dict['names']).drop(['names'], axis=1)

    @staticmethod
    def collect_dividends_data(json_container, comparison_years, comparison_number_of_datapoints):
        # Save first and last year of dividends dataset
        first_year = int(json_container["columnDefs_labels"][1])
        last_year = int(json_container["columnDefs_labels"][-4])

        # First case: both datasets start in same year AND same number of datapoints (compared to the previously
        # scraped datasets):
        if (first_year == comparison_years[0]) and (last_year == comparison_years[1]):
            dividends_list = json_container['rows'][0]['datum'][0:-3]
            payout_ratio_list = json_container['rows'][4]['datum'][0:-3]

        # Second case: both datasets start in same year BUT dividends datapoints < datapoints of previously scraped datasets
        elif first_year == comparison_years[0]:
            dividends_list = json_container['rows'][0]['datum'][0:comparison_number_of_datapoints]
            payout_ratio_list = json_container['rows'][4]['datum'][0:comparison_number_of_datapoints]

        # Third case: dividends dataset starts "later"
        # Assumption: dividends datapoints < datapoints of previously scraped datasets
        elif first_year > comparison_years[0]:
            years_difference = first_year - comparison_years[0]
            dividends_list = [np.nan for year in range(years_difference)]
            payout_ratio_list = [np.nan for year in range(years_difference)]
            dividends_list.extend(json_container['rows'][0]['datum'][years_difference:comparison_number_of_datapoints])
            payout_ratio_list.extend(
                json_container['rows'][4]['datum'][years_difference:comparison_number_of_datapoints])

        # Last case: dividends dataset starts "earlier"
        # Assumption: dividends datapoints < datapoints of previously scraped datasets
        elif first_year < comparison_years[0]:
            years_difference = comparison_years[0] - first_year
            dividends_list = json_container['rows'][0]['datum'][years_difference:comparison_number_of_datapoints]
            payout_ratio_list = json_container['rows'][4]['datum'][years_difference:comparison_number_of_datapoints]
            dividends_list.extend([np.nan for year in range(years_difference)])
            payout_ratio_list.extend([np.nan for year in range(years_difference)])

        dividends_dict = {'dividends': dividends_list, 'payout_ratio': payout_ratio_list}

        return pd.DataFrame(dividends_dict.values(), index=dividends_dict.keys(),
                            columns=[str(year) for year in range(comparison_years[0], comparison_years[1] + 1)],
                            dtype='float64')

    @staticmethod
    def collect_financials_data(json_container):
        financials_dict = {'revenue': json_container['incomeStatement']['rows'][0]['datum'][-2],
                           'operating_income': json_container['incomeStatement']['rows'][1]['datum'][-2],
                           'net_income': json_container['incomeStatement']['rows'][2]['datum'][-2],
                           'eps': json_container['incomeStatement']['rows'][5]['datum'][-2],
                           'operating_cash_flow': json_container['cashFlow']['rows'][0]['datum'][-2],
                           'free_cash_flow': json_container['cashFlow']['rows'][4]['datum'][-2]
                           }

        return pd.DataFrame(financials_dict.values(), index=financials_dict.keys(),
                            columns=[json_container['incomeStatement']['columnDefs'][-2]], dtype='float64')

    @staticmethod
    def scrape_and_combine_morningstar_data(morningstar_identifier, time_out_for_requests):
        scraped_data = MorningstarScraper.scrape_morningstar_data(morningstar_identifier, time_out_for_requests)

        growth_data = MorningstarScraper.collect_growth_data(scraped_data[0])
        efficiency_data = MorningstarScraper.collect_efficiency_data(scraped_data[1])
        financial_health_data = MorningstarScraper.collect_financial_health_data(scraped_data[2])
        cash_flow_data = MorningstarScraper.collect_cash_flow_data(scraped_data[3])
        dividends_data = MorningstarScraper.collect_dividends_data(scraped_data[4],
                                                [int(growth_data.columns[0]), int(growth_data.columns[-1])],
                                                int(growth_data.columns[-1]) - int(growth_data.columns[0]) + 1)

        dataset = pd.concat([growth_data, efficiency_data, financial_health_data, cash_flow_data,
                                        dividends_data], axis=0)

        financials_data = MorningstarScraper.collect_financials_data(scraped_data[5])

        metric_to_base_values = {
            'revenue': financials_data.loc['revenue'].iloc[-1] * 1000,
            'operating_income': financials_data.loc['operating_income'].iloc[-1] * 1000,
            'net_income': financials_data.loc['operating_income'].iloc[-1] * 1000,
            'eps': financials_data.loc['eps'].iloc[-1],
            'operating_cash_flow': financials_data.loc['operating_cash_flow'].iloc[-1] * 1000,
            'free_cash_flow': financials_data.loc['free_cash_flow'].iloc[-1] * 1000
        }

        dataset = DatabaseUtils.add_calculated_historical_values_to_dataset(metric_to_base_values, dataset)
        dataset = DatabaseUtils.add_estimated_historical_values_to_dataset(dataset)

        return dataset