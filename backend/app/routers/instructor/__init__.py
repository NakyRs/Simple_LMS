from fastapi import APIRouter
from app.routers.instructor import course, section, lesson 

router= APIRouter(prefix="/instructor")

router.include_router(course.router)
router.include_router(section.router)
router.include_router(lesson.router)