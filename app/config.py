from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    database_url: str = "postgresql://user:password@localhost:5432/fastapi_db"
    test_database_url: str = "postgresql://user:password@localhost:5432/fastapi_test_db"
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
