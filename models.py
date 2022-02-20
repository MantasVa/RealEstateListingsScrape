from enum import IntEnum

class Listing:
  def __init__(self, id, url, municipality, city, district, street, price, room_count, 
        space, floor, is_new_project, on_auction, status):
    self.id = id
    self.url = url
    self.municipality = municipality
    self.city = city
    self.district = district
    self.street = street
    self.price = price
    self.room_count = room_count
    self.space = space
    self.floor = floor
    self.is_new_project = is_new_project
    self.on_auction = on_auction
    self.status = status

  def to_object(self):
    return {'id': self.id, 'url': self.url, 'municipality': self.municipality, 'city': self.city,
       'district': self.district, 'street': self.street, 'price': self.price, 
       'roomCount': self.room_count, 'space': self.space, 'floor': self.floor,
        'isNewProject': self.is_new_project, 'onAuction': self.on_auction, 'status': self.status}

class Status(IntEnum):
    ACTIVE = 1
    RESERVED = 2
    SOLD = 3