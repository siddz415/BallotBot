import logging
import os
from datetime import timedelta
from typing import Optional

from cachetools import TTLCache, cached
from llama_index.core.callbacks import CallbackManager
from llama_index.core.indices import load_index_from_storage
from llama_index.core.storage import StorageContext
from pydantic import BaseModel, Field
from pymongo import MongoClient

logger = logging.getLogger("uvicorn")


class IndexConfig(BaseModel):
    callback_manager: Optional[CallbackManager] = Field(
        default=None,
    )


def get_index(config: IndexConfig = None):
    if config is None:
        config = IndexConfig()
    # connect to MongoDB
    mongo_uri = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://DemoAdmin:AWSHackathon@calicluster.vr4y6.mongodb.net/?retryWrites=true&w=majority&appName=CaliCluster",
    )
    db_name = os.getenv("MONGO_DB", "propositions_db")
    collection_name = os.getenv("MONGO_COLLECTION", "processed_chunks")

    logger.info(f"Connecting to MongoDB at {mongo_uri}...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    logger.info(f"Connected to MongoDB. Loading index from collection {collection_name}...")
    print(f"Connected to MongoDB. Loading index from collection {collection_name}...")
    
    storage_context = get_mongo_storage_context(collection)
    
    index = load_index_from_storage(
        storage_context, callback_manager=config.callback_manager
    )
    logger.info(f"Finished loading index from MongoDB collection {collection_name}")
    
    return index


@cached(
    TTLCache(maxsize=10, ttl=timedelta(minutes=5).total_seconds()),
    key=lambda *args, **kwargs: "global_mongo_storage_context",
)
def get_mongo_storage_context(collection) -> StorageContext:
    # Assuming that we use a custom StorageContext class that can handle MongoDB storage
    return StorageContext.from_mongo_collection(collection)
