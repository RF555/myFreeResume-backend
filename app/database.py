from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.config import settings

_client: AsyncMongoClient | None = None
_db: AsyncDatabase | None = None
_test_mode: bool = False


def set_test_mode(enabled: bool = True) -> None:
    global _test_mode
    _test_mode = enabled


async def connect_db(test: bool = False) -> None:
    global _client, _db
    use_test = test or _test_mode
    _client = AsyncMongoClient(settings.mongodb_uri)
    db_name = "myFreeResume_test" if use_test else "myFreeResume"
    _db = _client[db_name]

    await _db.users.create_index("email", unique=True)
    await _db.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)
    await _db.refresh_tokens.create_index([("user_id", 1), ("token_hash", 1)])
    await _db.job_types.create_index("user_id")
    await _db.entries.create_index([("user_id", 1), ("job_type_id", 1)])


async def close_db() -> None:
    global _client, _db
    if _client:
        await _client.close()
    _client = None
    _db = None


def get_db() -> AsyncDatabase:
    if _db is None:
        raise RuntimeError("Database not connected")
    return _db
