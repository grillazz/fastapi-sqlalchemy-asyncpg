import asyncio
import os
import sys

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)

from the_app.models.base import Base as app_base

target_metadata = app_base.metadata


def do_run_migrations(connection):
    context.configure(connection=connection,
                      target_metadata=target_metadata,
                      include_schemas=True,
                      version_table_schema=target_metadata.schema)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = f"postgresql+asyncpg://user:secret@db:5432/devdb"
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


asyncio.run(run_migrations_online())
