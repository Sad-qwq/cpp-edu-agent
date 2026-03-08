import asyncio
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Ensure backend directory on path for app imports
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(PROJECT_ROOT))

from app.core.config import settings

async def add_columns():
    print(f"Connecting to database at {settings.DATABASE_URL}...")
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        print("Adding bio column if missing...")
        await conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS bio VARCHAR;'))
        print("Adding avatar_url column if missing...")
        await conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS avatar_url VARCHAR;'))

        # Announcement schema backfill for existing databases.
        print("Adding announcement.is_pinned column if missing...")
        await conn.execute(
            text(
                'ALTER TABLE "announcement" '
                'ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN NOT NULL DEFAULT FALSE;'
            )
        )
        print("Adding announcement.is_active column if missing...")
        await conn.execute(
            text(
                'ALTER TABLE "announcement" '
                'ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;'
            )
        )
    await engine.dispose()
    print("Done.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_columns())
