from src.database.damodaran_scraper import DamodaranScraper
from src.database.morningstar_scraper import MorningstarScraper
from src.utils.excel_importer import ExcelImporter

def main():
    # Import data
    morningstar_identifier = '0P000000GY'
    scraped_dataset = MorningstarScraper.scrape_and_combine_morningstar_data(morningstar_identifier, 10.0)
    scraped_dataset.to_csv('../data/aapl_dataset.csv')

if __name__ == "__main__":
    main()