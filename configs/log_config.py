from os import path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="LOG_", env_file_encoding="utf8", strict=False
    )

    LEVEL: str
    PATH: str = (
        path.dirname(path.dirname((path.abspath(__file__))))
        + "/logs/fastapi-{time:YYYY-MM-DD}.log"
    )
    RETENTION: str


log_settings = Settings()