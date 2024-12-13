import pandas as pd
import ssl
import time

class DamodaranScraper:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def scrape_data():
        """Function to get data from http://pages.stern.nyu.edu/~adamodar/"""

        # Prerequisites to avoid SSL certification error
        ssl._create_default_https_context = ssl._create_unverified_context

        # Define URLs to retrieve data from:
        # Table 'Ratings, Spreads and Interest Coverage Ratios'
        spread_url = 'https://pages.stern.nyu.edu/~adamodar/pc/ratings.xls'
        # Table 'Risk Premiums for Other Markets'
        risk_premiums_url = 'https://pages.stern.nyu.edu/~adamodar/pc/datasets/ctryprem.xlsx'

        # Get data. Pause between both tables to avoid excessive webscraping:
        spread_table = pd.read_excel(spread_url, sheet_name=0, skiprows=17, header=0, nrows=15, usecols='A:D,F:I')
        time.sleep(5.0)
        risk_premiums = pd.read_excel(risk_premiums_url, sheet_name='Regional Simple Averages', skiprows=3, header=0,
                                      nrows=9, usecols='A,C')

        return spread_table, risk_premiums

    @staticmethod
    def modify_damodaran_data(spread_df, risk_premiums_df):
        # Modify the dataframes to obtain relevant data:
        spread_nonfinancials = spread_df.iloc[:, :4]
        spread_nonfinancials.columns = ["greater_than", "lower_equal_than", "rating", "spread"]
        spread_financials = spread_df.iloc[:, 4:8]
        spread_financials.columns = ["greater_than", "lower_equal_than", "rating", "spread"]

        risk_premiums_df.columns = ["region", "ERP"]

        return spread_nonfinancials, spread_financials, risk_premiums_df