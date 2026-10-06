from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from database import Base

BACKEND = Path(__file__).resolve().parent.parent


def alembic_config(url: str) -> Config:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    config.set_main_option("sqlalchemy.url", url)
    return config


@pytest.fixture()
def db_url(tmp_path):
    # Archivo temporal: así se prueba exactamente lo que haría Alembic en una base de datos real
    return f"sqlite:///{tmp_path / 'migraciones.db'}"


def test_there_is_a_single_migration_head():
    # Dos cabezas = dos personas (o dos ramas) crearon migraciones a la vez: hay que fusionarlas
    heads = ScriptDirectory.from_config(alembic_config("sqlite://")).get_heads()
    assert len(heads) == 1


def test_upgrade_head_creates_the_schema(db_url):
    command.upgrade(alembic_config(db_url), "head")
    tables = set(inspect(create_engine(db_url)).get_table_names())
    assert {"users", "expenses", "alembic_version"} <= tables


def test_migrations_match_the_models(db_url):
    """Si cambias un modelo y olvidas crear la migración, este test falla."""
    command.upgrade(alembic_config(db_url), "head")
    engine = create_engine(db_url)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        differences = compare_metadata(context, Base.metadata)
    assert differences == []


def test_downgrade_to_base_removes_the_tables(db_url):
    config = alembic_config(db_url)
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    tables = set(inspect(create_engine(db_url)).get_table_names())
    assert "users" not in tables
    assert "expenses" not in tables
