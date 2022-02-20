from selenium import webdriver
from bs4 import BeautifulSoup
import uuid
from models import Listing, Status
from logging import Logger

class Scraper:
    def __init__(self, driver: webdriver, base_url: str, logger: Logger):
        self.driver = driver
        self.base_url = base_url
        self.logger = logger

    def get_page_count(self) -> int:
        self.driver.get(self.base_url)
        content = self.driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        paginationLinks = soup.findAll('a', attrs={'class':'page-bt'})
        pageCount = None

        try:
            pageCount = int(paginationLinks[len(paginationLinks)-2].get_text())
            self.logger.info(f'Got listings page count {pageCount}')    
        except:
            self.logger.error('Page count cannot be parsed.', paginationLinks)
        
        if pageCount is not None: return pageCount 
        else: return 0

    def extractListings(self, page_number = '') -> list:
        self.driver.get(f'{self.base_url}/{page_number}')
        content = self.driver.page_source
        pageSoup = BeautifulSoup(content, 'html.parser')

        pageListings = []
        for row in pageSoup.findAll('tr', attrs={'class':'list-row'}):
            img = row.find('td', attrs={'class':'list-img'})
            if img is not None:
                (url, city, district, municipality, street) = self.get_listing_location(row)
                price = self.get_listing_price(row)
                rooms = self.get_listing_room_count(row)
                space = self.get_listing_space(row)
                floor = self.get_listing_floor_number(row)
                is_new_proj, on_auction = self.get_listing_extra_info(row)    
                status = self.get_listing_status(row)          

                pageListings.append(Listing(str(uuid.uuid4()), url, municipality, city, district, street, price, 
                    rooms, space, floor, is_new_proj, on_auction, status))
        return pageListings

    def get_listing_location(self, listing):
        urlColumn = listing.find('td', attrs={'class':'list-adress'})
        url = None; city = '-'; district = None; municipality = None; street = None
        if urlColumn is None:
            self.logger.error("Could not find url column.", listing)
        else:    
            url = urlColumn.a['href']
            location = urlColumn.a.contents[0].strip()
            if ',' in location:
                locationList = location.split(',')
                if 'r.' in location or 'sav.' in location:
                    municipality = locationList[0]
                    city = locationList[1]
                else:
                    city = locationList[0]
                    district = locationList[1]
            else:
                city = location
                street = urlColumn.br.next_sibling.strip()

        return (url, city, district, municipality, street)

    def get_listing_price(self, listing):
        priceTag = listing.find('span', attrs={'class':'list-item-price'})
        price = None
        if priceTag is None:
            self.logger.error("Could not find price column.", listing)
        else:
            try:
                price = int(priceTag.get_text().replace('€', '').replace(' ', ''))
            except:
                self.logger.error("Could not parse object price.", priceTag)
        return price

    def get_listing_room_count(self, listing):
        roomsTag = listing.find('td', attrs={'class':'list-RoomNum'})
        if roomsTag is None:
            rooms = None
            self.logger.error("Could not find rooms column.", listing)
        else:
            rooms = roomsTag.get_text().strip()
        return rooms

    def get_listing_space(self, listing):
        spaceTag = listing.find('td', attrs={'class':'list-AreaOverall'})
        if spaceTag is None:
            space = None
            self.logger.error("Could not find space column.", listing)
        else:
            space = spaceTag.get_text().strip()
        return space

    def get_listing_floor_number(self, listing):
        floorTag = listing.find('td', attrs={'class':'list-Floors'})
        if floorTag is None:
            floor = None
            self.logger.error("Could not find floor column.", listing)
        else:
            floor = floorTag.get_text().strip()
        return floor    
        
    def get_listing_status(self, listing):
        if listing.find('div', attrs={'class':'list-row-sold1-lt'}) is not None: status = Status.SOLD
        elif listing.find('div', attrs={'class':'reservation-strip'}) is not None: status = Status.RESERVED
        else: status = Status.ACTIVE
        return status

    def get_listing_extra_info(self, listing):
        if listing.find('div', attrs={'class':'in-project'}) is not None: newProj = True
        else: newProj = False

        if listing.find('div', attrs={'class':'city-strip'}) is not None: onAuction = True
        else: onAuction = False
        return newProj,onAuction          