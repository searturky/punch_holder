from app.api.v1.routers import register
from fastapi import APIRouter

router = APIRouter()

router.include_router(register.router, prefix="/user")
