from motor.motor_asyncio import AsyncIOMotorClient
from db.settings.creds import creds

_client: AsyncIOMotorClient | None = None

def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(creds.mongodb_conn_string)
    return _client

def close_client():
    global _client
    if _client:
        _client.close()
        _client = None

async def create_tasks_results_idx():
    collection = get_client()[creds.MONGO_DB_NAME]['tasks_results']
    await collection.create_index("req_id", unique=True)
