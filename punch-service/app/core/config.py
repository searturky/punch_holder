from typing import Dict, List, Union
from pydantic import BaseSettings, validator


class Settings(BaseSettings):

    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[str] = []
    SERVICE_ENV: str
    PGSQL_URL: str
    SCHEDULER_PGSQL_URL: str
    SUPERUSER_KEY: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DOCS_URL: str
    OPENAPI_URL: str

    TIMEZONE: str = "Asia/Shanghai"

    class Config:
        case_sensitive = True
        env_file = '.env', '.env.prod'
        env_file_encoding = 'utf-8'

    # @validator("BACKEND_CORS_ORIGINS", pre=True)
    # @classmethod
    # def assemble_cors_origins(cls, value: Union[str, List[str]]) -> Union[List[str], str]:
    #     if isinstance(value, str) and not value.startswith("["):
    #         return [i.strip() for i in value.split(",")]

    #     if isinstance(value, (list, str)):
    #         return value

    #     raise ValueError(value)


settings = Settings()
