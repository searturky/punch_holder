from typing import Dict, List, Union
from pydantic import BaseSettings, validator


class Settings(BaseSettings):

    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[str] = []
    SERVICE_ENV: str
    MONGODB_URL: str
    APSCHEDULER_MONGODB_URL: str

    class Config:
        case_sensitive = True
        env_file = '.env', '.env.prod'
        env_file_encoding = 'utf-8'

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            return cls.json_loads(raw_val)

    # @validator("BACKEND_CORS_ORIGINS", pre=True)
    # @classmethod
    # def assemble_cors_origins(cls, value: Union[str, List[str]]) -> Union[List[str], str]:
    #     if isinstance(value, str) and not value.startswith("["):
    #         return [i.strip() for i in value.split(",")]

    #     if isinstance(value, (list, str)):
    #         return value

    #     raise ValueError(value)


settings = Settings()
pass
