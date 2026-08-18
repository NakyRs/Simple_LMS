from fastapi import APIRouter
from app.routers.student import course

router= APIRouter()

router.include_router(course.router)