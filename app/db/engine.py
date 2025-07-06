import os
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# docker-compose already exports DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///./data/tickets.db"
)

# echo=False → keep logs clean; future=True → 2.0 style API
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
