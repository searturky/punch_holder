from app.api.v1.routers import register, user
from fastapi import APIRouter

router = APIRouter()

router.include_router(register.router, prefix="/register")
router.include_router(user.router, prefix="/user")