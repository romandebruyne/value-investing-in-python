import pandas as pd
import yfinance as yf
from src.utils.data_interval import DataInterval
from src.utils.assessment_period import AssessmentPeriod

class YahooFinanceScraper:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def scrape_price_data(ticker, period, interval):
        # Check period
        if period not in ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']:
            print('Invalid yahoo finance period.')
            return

        # Check interval
        if interval.value not in [i.value for i in DataInterval]:
            print('Invalid interval.')
            return

        price_data = yf.download(ticker, period=period, interval=interval.value, multi_level_index=False,
                                 progress=False)
        price_data.dropna(subset=['Adj Close'], axis=0, how='any', inplace=True)

        # Convert and return data
        return pd.DataFrame(price_data['Adj Close'], index=price_data.index)