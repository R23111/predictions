from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = ""
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    DATABASE_URI: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if v and isinstance(v, str):
            return v
        postgres_dsn = PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            path=f"{info.data.get('POSTGRES_DB') or ''}",
        )
        return str(postgres_dsn)

    class ConfigDict:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
