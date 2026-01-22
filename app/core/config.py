from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "News Near Me API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Keys
    gemini_api_key: str
    
    # Geolocation
    geolocation_api_url: str = "http://ip-api.com/json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()