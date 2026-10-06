import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_DATABASE_URL = "sqlite:///./expenses.db"
DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
DEFAULT_TOKEN_MINUTES = 30
MIN_SECRET_KEY_LENGTH = 32


@dataclass(frozen=True)
class Settings:
    secret_key: str
    database_url: str
    cors_origins: list[str]
    access_token_expire_minutes: int


def parse_origins(text: str) -> list[str]:
    """'http://a.com, http://b.com,' -> ['http://a.com', 'http://b.com']"""
    return [origin.strip() for origin in text.split(",") if origin.strip()]


def load_settings(env: Mapping[str, str]) -> Settings:
    """Lee la configuración de un diccionario de variables de entorno y la valida."""
    secret_key = env.get("SECRET_KEY", "").strip()
    if not secret_key:
        raise RuntimeError(
            "Falta SECRET_KEY. Copia .env.example a .env y genera una clave con: "
            "openssl rand -hex 32"
        )
    if len(secret_key) < MIN_SECRET_KEY_LENGTH:
        raise RuntimeError(
            f"SECRET_KEY es demasiado corta (mínimo {MIN_SECRET_KEY_LENGTH} caracteres). "
            "Genera una con: openssl rand -hex 32"
        )

    minutes_text = env.get("ACCESS_TOKEN_EXPIRE_MINUTES", str(DEFAULT_TOKEN_MINUTES))
    try:
        minutes = int(minutes_text)
    except ValueError:
        minutes = 0
    if minutes <= 0:
        raise RuntimeError(
            "ACCESS_TOKEN_EXPIRE_MINUTES debe ser un número entero mayor que 0 "
            f"(valor recibido: {minutes_text!r})"
        )

    return Settings(
        secret_key=secret_key,
        database_url=env.get("DATABASE_URL", DEFAULT_DATABASE_URL),
        cors_origins=parse_origins(env.get("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)),
        access_token_expire_minutes=minutes,
    )


# Una variable que ya esté definida en el sistema tiene prioridad sobre el archivo .env
load_dotenv()
settings = load_settings(os.environ)