from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy
from fastapi import Depends
from app.config import settings


def get_cosmosdb_client() -> CosmosClient:
    """Create and return a CosmosDB client."""
    # Get connection details from environment variables
    endpoint = settings.COSMOS_DB_ENDPOINT
    primary_key = settings.COSMOS_DB_PRIMARY_KEY

    # Create Cosmos DB client
    cosmosdb_client = CosmosClient(endpoint, primary_key)

    return cosmosdb_client


def get_database(client: CosmosClient = Depends(get_cosmosdb_client)) -> DatabaseProxy:
    """Get a CosmosDB database instance."""
    database_name = settings.COSMOS_DB_DATABASE_NAME
    database = client.get_database_client(database_name)

    return database


async def get_container(
    container_name: str, database: DatabaseProxy = Depends(get_database)
) -> ContainerProxy:
    """Get a CosmosDB container instance."""
    container = database.get_container_client(container_name)

    return container
