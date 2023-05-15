from collections import defaultdict
import os
import json
from typing import Dict, List, Union
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[str] = []
    SERVICE_ENV: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(value, str) and not value.startswith("["):
            return [i.strip() for i in value.split(",")]

        if isinstance(value, (list, str)):
            return value

        raise ValueError(value)

    MONGODB_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
