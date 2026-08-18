from fastapi import APIRouter
from app.routers.user import user

router= APIRouter()

router.include_router(user.router)