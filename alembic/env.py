from __future__ import annotations

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import os

# Alembic Config object, provides access to values in alembic.ini
config = context.config

# Configure Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Import app settings & metadata ---
# prepend_sys_path = . in alembic.ini should already allow "app.*" imports
from app.core.config import settings
from app.db.base import Base
import app.models  # IMPORTANT: ensures models are imported so metadata has all tables

target_metadata = Base.metadata

# If alembic.ini has empty sqlalchemy.url, fill it from app settings
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
