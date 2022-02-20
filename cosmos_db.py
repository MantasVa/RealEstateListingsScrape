from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy
from logging import Logger
import calendar
from datetime import datetime, date, timezone

def get_cosmos_container(endpoint, key, dbName, containerName, partitionKey) -> ContainerProxy:
  client = CosmosClient(endpoint, key)
  database = client.create_database_if_not_exists(id=dbName)
  container = database.create_container_if_not_exists(
    id=containerName,
    partition_key=PartitionKey(path=partitionKey),
  )
  return container

def add_items(container: ContainerProxy, items: list, logger: Logger) -> None:
  logger.debug('Starting to add listings to cosmos db')
  for item in items:
    add_item(container, item.to_object())
  logger.debug('Finished adding listings to cosmos db')

def add_item(container, listing) -> None:
  container.create_item(body=listing)

def clean_duplicate_listings(container: ContainerProxy, logger: Logger) -> None:
  logger.debug("Starting cleaning duplicate listings")

  year = date.today().year
  month = date.today().month
  _, last_day = calendar.monthrange(year, month)
  fromTs = datetime(year, month, 1, tzinfo=timezone.utc).timestamp()
  toTs = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc).timestamp()

  logger.debug(f"Calculated timestamps for duplicate search: From: {fromTs}, To: {toTs}.")

  items = list(container.query_items(
      query= f"""SELECT l.id, l.url, l.city FROM Listings l 
      WHERE l._ts >= {fromTs} AND l._ts <= {toTs}""",
      enable_cross_partition_query=True
  ))

  seen = list()
  duplicateCount = 0
  for item in items:
    if any(item['url'] == s['url'] for s in seen):
      container.delete_item(item['id'], partition_key=item['city'])
      duplicateCount += 1
    else:
      seen.append(item)

  logger.info(f"Found and deleted {duplicateCount} listings.")
