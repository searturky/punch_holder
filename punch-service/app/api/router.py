from app.api.v1 import router as v1
from fastapi import APIRouter, Request

router = APIRouter()
router.include_router(v1.router, prefix="/v1")


@router.post("/actuator/health")
async def health():
    return {"status": "OK"}


@router.post("/actuator/echo")
async def echo(request: Request):
    json_body = await request.json()
    print("echo: %s", json_body)
    return {
        "status": "OK",
        "body": json_body,
    }