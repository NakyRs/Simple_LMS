from fastapi import APIRouter
from app.routers.admin import enrollment

router= APIRouter()

router.include_router(enrollment.router)