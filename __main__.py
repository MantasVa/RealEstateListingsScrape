from typing import Final
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import yaml

import log_config
from scraper import Scraper
import cosmos_db

CONFIG_FILE_PATH: Final = './config.yaml'

def read_config():
    with open(CONFIG_FILE_PATH, 'r') as f:
        return yaml.safe_load(f)

def main():
    config = read_config()

    logger = log_config.getLogger(aiKey=config["AI_INSTRUMENTATION_KEY"])
    logger.error(f'Starting NT scrape function {datetime.today()}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    scraper = Scraper(driver, base_url = config["START_URL"], logger = logger)
    pageCount = scraper.get_page_count()

    listings = []
    if pageCount > 0:
        for x in range(1, pageCount + 1):
            listings += scraper.extractListings(x)
    else:
        logger.error('Page count not found, scraping only this page')
        listings = scraper.extractListings()
    driver.quit()    

    endpoint = config["DB_ENDPOINT"]
    key = config["DB_KEY"]
    database_name = config["DB_DATABASE_NAME"]
    container_name = config["DB_CONTAINER_NAME"]
    partition_key = config["CN_PARTITION_KEY"]
    container = cosmos_db.get_cosmos_container(endpoint, key, database_name, container_name, partition_key)
    cosmos_db.add_items(container, listings, logger)
    cosmos_db.clean_duplicate_listings(container, logger)

    logger.info(f'Stopping NT scrape function {datetime.today()}. Found {len(listings)} listings.')

if __name__ == "__main__":
    main()