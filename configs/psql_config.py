from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="DB_", strict=False, env_file_encoding="utf8"
    )
    HOST: str
    PORT: str
    NAME: str
    USER: str
    PASSWORD: str

    @property
    def DSN(self):
        return f"postgres://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

psql_settings = Settings()