from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy

def getCosmosContainer(endpoint, key, dbName, containerName, partitionKey) -> ContainerProxy:
  client = CosmosClient(endpoint, key)
  database = client.create_database_if_not_exists(id=dbName)
  container = database.create_container_if_not_exists(
    id=containerName,
    partition_key=PartitionKey(path=partitionKey),
  )
  return container

def addItem(container, listing) -> None:
  container.create_item(body=listing)

def cleanContainer(container) -> None:
  items = list(container.query_items(
      query= "SELECT * FROM Listings",
      enable_cross_partition_query=True
  ))
  for item in items:
    container.delete_item(item['id'], partition_key=item['district'])