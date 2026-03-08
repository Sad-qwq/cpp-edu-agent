from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def _column_exists(conn: AsyncConnection, table_name: str, column_name: str) -> bool:
    query = text(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = :table_name AND column_name = :column_name
        LIMIT 1
        """
    )
    result = await conn.execute(query, {"table_name": table_name, "column_name": column_name})
    return result.first() is not None


async def _add_column_if_missing(conn: AsyncConnection, table_name: str, column_name: str, definition: str) -> None:
    if await _column_exists(conn, table_name, column_name):
        return
    await conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {definition}'))


async def apply_manual_migrations(conn: AsyncConnection) -> None:
    await _add_column_if_missing(conn, "problem", "display_order", "INTEGER DEFAULT 0")
    await _add_column_if_missing(conn, "problem", "options", "JSON")
    await _add_column_if_missing(conn, "problem", "correct_answer", "VARCHAR")
    await _add_column_if_missing(conn, "problem", "code_template", "TEXT")
    await _add_column_if_missing(conn, "problem", "test_cases", "JSON")
