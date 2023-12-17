from pydantic_settings import BaseSettings, SettingsConfigDict
from hashlib import sha256
from os import urandom


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="UTF8", env_prefix="AUTH_", strict=False
    )

    ALGORITHM: str
    SECRETS_KEY: str
    ACCESS_TOKEN_EXP_HOURS: int


auth_settings = Settings()