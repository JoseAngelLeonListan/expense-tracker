import pytest

from config import DEFAULT_DATABASE_URL, load_settings, parse_origins, settings

KEY = "x" * 40


def env(**extra):
    return {"SECRET_KEY": KEY, **extra}


def test_defaults():
    result = load_settings(env())
    assert result.secret_key == KEY
    assert result.database_url == DEFAULT_DATABASE_URL
    assert result.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173"]
    assert result.access_token_expire_minutes == 30


def test_missing_secret_key_gives_a_clear_error():
    with pytest.raises(RuntimeError, match="Falta SECRET_KEY"):
        load_settings({})


def test_blank_secret_key_is_rejected():
    with pytest.raises(RuntimeError, match="Falta SECRET_KEY"):
        load_settings({"SECRET_KEY": "   "})


def test_short_secret_key_is_rejected():
    with pytest.raises(RuntimeError, match="demasiado corta"):
        load_settings({"SECRET_KEY": "corta"})


def test_custom_database_url():
    url = "postgresql+psycopg://u:p@localhost:5432/db"
    assert load_settings(env(DATABASE_URL=url)).database_url == url


def test_parse_origins_trims_spaces_and_ignores_empty_items():
    assert parse_origins(" http://a.com , http://b.com ,, ") == ["http://a.com", "http://b.com"]


def test_cors_origins_from_env():
    result = load_settings(env(CORS_ORIGINS="https://miapp.example, http://localhost:3000"))
    assert result.cors_origins == ["https://miapp.example", "http://localhost:3000"]


def test_empty_cors_origins_means_none_allowed():
    # Mejor bloquear de más que dejar pasar a todo el mundo por un valor vacío
    assert load_settings(env(CORS_ORIGINS="")).cors_origins == []


def test_token_minutes_from_env():
    assert load_settings(env(ACCESS_TOKEN_EXPIRE_MINUTES="60")).access_token_expire_minutes == 60


@pytest.mark.parametrize("value", ["abc", "0", "-5", "", "1.5"])
def test_invalid_token_minutes_are_rejected(value):
    with pytest.raises(RuntimeError, match="ACCESS_TOKEN_EXPIRE_MINUTES"):
        load_settings(env(ACCESS_TOKEN_EXPIRE_MINUTES=value))


def test_tests_run_with_the_in_memory_database():
    # conftest.py fija estas variables antes de importar la app
    assert settings.database_url == "sqlite://"