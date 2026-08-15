from fastapi import APIRouter
from app.routers.instructor import course, lesson, module 

router= APIRouter()

router.include_router(course.router)
router.include_router(module.router)
router.include_router(lesson.router)