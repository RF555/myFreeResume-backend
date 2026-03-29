import os
from collections.abc import AsyncGenerator

os.environ["RATE_LIMIT_ENABLED"] = "false"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import set_test_mode, get_db, connect_db, close_db

set_test_mode(True)

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    await connect_db(test=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    try:
        db = get_db()
        for name in await db.list_collection_names():
            await db[name].delete_many({})
    except RuntimeError:
        pass
    await close_db()
