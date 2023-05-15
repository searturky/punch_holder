import httpx
import os
from enum import Enum
from typing import Dict
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

__all__ = ["get_http_client", "AirByteUrl", "URLBaseModel"]

_AIRBYTE_URL = os.environ.get("AIRBYTE_URL")

@asynccontextmanager
async def get_http_client():
    http_client = None
    try:
        http_client = httpx.AsyncClient()
        yield http_client
    finally:
        if http_client:
            await http_client.aclose()


class AirByteUrl(str, Enum):

    ListAllSourceDefinitions = "/api/v1/source_definitions/list"
    ListAllDestinations = "/api/v1/destinations/list"
    ListAllSources = "/api/v1/sources/list"
    ListAllConnections = "/api/v1/connections/list"
    SourceDefinitionSpecification = "/api/v1/source_definition_specifications/get"
    CheckSourceConnection = "/api/v1/scheduler/sources/check_connection"
    CreateSource = "/api/v1/sources/create"
    SourcesSchema = "/api/v1/sources/discover_schema"
    CreateConnection = "/api/v1/web_backend/connections/create"
