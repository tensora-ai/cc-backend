from azure.cosmos import CosmosClient, DatabaseProxy
import os

# Initialize CosmosDB client
client = CosmosClient(url=os.getenv("COSMOS_DB_ENDPOINT"), credential=os.getenv("COSMOS_DB_PRIMARY_KEY"))

# Get a reference to the database
database = client.get_database_client(os.getenv("COSMOS_DB_DATABASE_NAME"))

async def get_database() -> DatabaseProxy:
    return database