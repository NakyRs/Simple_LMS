from fastapi import APIRouter
from app.routers.instructor import course, section, lesson, forum

router= APIRouter(prefix="/instructor")

router.include_router(course.router)
router.include_router(section.router)
router.include_router(lesson.router)
router.include_router(forum.router)