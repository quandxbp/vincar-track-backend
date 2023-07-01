from bson import ObjectId
from pymongo.errors import WriteError

import app.main as main
from app.routers.exceptions import AlreadyExistsHTTPException


async def get_mongo_meta() -> dict:
    list_databases = await main.app.state.mongo_client.list_database_names()
    list_of_collections = {}
    for db in list_databases:
        list_of_collections[db] = await main.app.state.mongo_client[db].list_collection_names()
    mongo_meta = await main.app.state.mongo_client.server_info()
    return {"version": mongo_meta["version"], "databases": list_databases, "collections": list_of_collections}
