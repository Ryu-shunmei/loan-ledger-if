from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="APP_", env_file_encoding="utf8", strict=False
    )

    NAME: str
    MODE: str
    DEBUG: bool

    @property
    def DOCS(self) -> bool:
        if self.MODE.lower() == "dev":
            return "/"
        else:
            return None

    @property
    def OPENAPI(self) -> bool:
        if self.MODE.lower() == "dev":
            return "/openapi.json"
        else:
            return None


app_settings = Settings()