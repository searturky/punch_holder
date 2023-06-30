from fastapi import APIRouter
from app.api.v1.routers import task, user, token, key

router = APIRouter()

router.include_router(task.router, prefix="/task")
router.include_router(user.router, prefix="/user")
router.include_router(token.router, prefix="/token")
router.include_router(key.router, prefix="/key")
