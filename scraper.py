from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from datetime import datetime
import uuid
import yaml

import logConfig
import cosmosDb
from models import Listing, Status 

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

config = read_yaml('./config.yaml')

logger = logConfig.getLogger(aiKey=config["AI_INSTRUMENTATION_KEY"])
logger.error(f'Starting NT scrape function {datetime.today()}')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
baseUrl = config["START_URL"]
driver.get(f'{baseUrl}/1')
content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')
paginationLinks = soup.findAll('a', attrs={'class':'page-bt'})
pageCount = None

try:
    pageCount = int(paginationLinks[len(paginationLinks)-2].get_text())
    logger.info(f'Got listings page count {pageCount}')    
except:
    logger.error('Page count cannot be parsed.', paginationLinks)

def extractListingsFromPage(pageSoup) -> list:
    pageListings = []
    for row in pageSoup.findAll('tr', attrs={'class':'list-row'}):
        img = row.find('td', attrs={'class':'list-img'})
        if img is not None:
            urlColumn = row.find('td', attrs={'class':'list-adress'})
            if urlColumn is None:
                url = None; district = 'Not Found'; street = None
                logger.error("Could not find url column.", row)
            else:    
                url = urlColumn.a['href']
                district = urlColumn.a.contents[0].strip()
                street = urlColumn.br.next_sibling.strip()

            priceTag = row.find('span', attrs={'class':'list-item-price'})
            price = None
            if priceTag is None:
                logger.error("Could not find price column.", row)
            else:
                try:
                    price = int(priceTag.get_text().replace('€', '').replace(' ', ''))
                except:
                    logger.error("Could not parse object price.", priceTag)

            roomsTag = row.find('td', attrs={'class':'list-RoomNum'})
            if roomsTag is None:
                rooms = None
                logger.error("Could not find rooms column.", row)
            else:
                rooms = roomsTag.get_text().strip()

            spaceTag = row.find('td', attrs={'class':'list-AreaOverall'})
            if spaceTag is None:
                space = None
                logger.error("Could not find space column.", row)
            else:
                space = spaceTag.get_text().strip()

            floorTag = row.find('td', attrs={'class':'list-Floors'})
            if floorTag is None:
                floor = None
                logger.error("Could not find floor column.", row)
            else:
                floor = floorTag.get_text().strip()

            if row.find('div', attrs={'class':'in-project'}) is not None: newProj = True
            else: newProj = False

            if row.find('div', attrs={'class':'city-strip'}) is not None: onAuction = True
            else: onAuction = False    

            if row.find('div', attrs={'class':'list-row-sold1-lt'}) is not None: status = Status.SOLD
            elif row.find('div', attrs={'class':'reservation-strip'}) is not None: status = Status.RESERVED
            else: status = Status.ACTIVE          

            pageListings.append(Listing(str(uuid.uuid4()), url, district, street, price, 
                rooms, space, floor, newProj, onAuction, status))
    return pageListings        

apartments = []
if paginationLinks is None or pageCount is None:
    apartments = extractListingsFromPage(soup)
else:
    for x in range(1, pageCount):
        if x == 1:
            apartments = extractListingsFromPage(soup) 
        else:   
            driver.get(f'{baseUrl}/{x}')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            apartments = apartments + extractListingsFromPage(soup)
driver.close()

logger.debug('Starting to add listings to cosmos db')

container = cosmosDb.getCosmosContainer(
    config["DB_ENDPOINT"], config["DB_KEY"], config["DB_DATABASE_NAME"],
    config["DB_CONTAINER_NAME"], config["CN_PARTITION_KEY"])

for ap in apartments:
    cosmosDb.addItem(container, ap.toObject())

logger.debug('Finished adding listings to cosmos db')

logger.info(f'Stopping NT scrape function {datetime.today()}. Found {len(apartments)} listings.')