from enum import IntEnum

class Status(IntEnum):
    ACTIVE = 1
    RESERVED = 2
    SOLD = 3

class Listing:
  def __init__(self, id: str, url: str, municipality: str, city: str, district: str, street: str,
   price: float, room_count: int, space: float, floor: int, floors_count: int, 
   is_new_project: bool, on_auction: bool, status: Status):
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
    self.floors_count = floors_count
    self.is_new_project = is_new_project
    self.on_auction = on_auction
    self.status = status