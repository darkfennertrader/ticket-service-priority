"""
Run once inside the `init-db` container defined in docker-compose.yml.
Creates the tickets table if it does not exist.
"""

import asyncio
from app.db.engine import engine
from app.db.schema import metadata


async def main() -> None:
    async with engine.begin() as conn:
        # Uses SQLAlchemy's DDL generator
        await conn.run_sync(metadata.create_all)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
