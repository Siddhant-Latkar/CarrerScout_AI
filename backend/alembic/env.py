from logging.config import fileConfig

from sqlalchemy import create_engine, pool

import app.database.models  # noqa: F401
from alembic import context
from app.core.config import settings
from app.database.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic compares this metadata with the database to build migrations.
target_metadata = Base.metadata


def run_migrations_online() -> None:
    """Run migrations against the live database from our settings."""
    engine = create_engine(settings.database_url, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations are not supported. Run against a live database.")

run_migrations_online()
