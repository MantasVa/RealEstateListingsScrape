from enum import IntEnum

class Listing:
  def __init__(self, id, url, district, street, price, roomCount, 
        space, floor, isNewProject, onAuction, status):
    self.id = id
    self.url = url
    self.district = district
    self.street = street
    self.price = price
    self.roomCount = roomCount
    self.space = space
    self.floor = floor
    self.isNewProject = isNewProject
    self.onAuction = onAuction
    self.status = status

  def toObject(self):
    return {'id': self.id, 'url': self.url, 'district': self.district, 'street': self.street, 
        'price': self.price, 'roomCount': self.roomCount, 'space': self.space, 'floor': self.floor,
        'isNewProject': self.isNewProject, 'onAuction': self.onAuction, 'status': self.status}

class Status(IntEnum):
    ACTIVE = 1
    RESERVED = 2
    SOLD = 3