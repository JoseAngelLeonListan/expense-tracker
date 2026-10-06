from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import models  # noqa: F401  (importarlo registra las tablas en Base.metadata)
from config import settings
from database import Base

config = context.config

if config.config_file_name is not None:
    # disable_existing_loggers=False: no silenciar los logs de la aplicación ni de pytest
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Alembic compara esto con la base de datos para generar migraciones automáticas
target_metadata = Base.metadata


def get_url() -> str:
    # Si alguien fija la URL por código (los tests), se respeta; si no, la de config.py
    return config.get_main_option("sqlalchemy.url") or settings.database_url


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse a la base de datos (alembic upgrade head --sql)."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Se conecta a la base de datos y aplica las migraciones."""
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # detecta también cambios de tipo (Float -> Numeric)
            # SQLite casi no sabe modificar tablas: Alembic las reconstruye en modo "batch"
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
