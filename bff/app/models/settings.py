from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    auth0_client_id: str
    auth0_client_secret: str
    auth0_domain: str
    auth0_audience: str
    auth0_callback_url: str
    app_secret_key: str
    app_secret_salt: str
    redis_url: str
    backend_url: str
    environment: str = "development"
