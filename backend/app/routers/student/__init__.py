from fastapi import APIRouter
from app.routers.student import course, assignment, forum

router= APIRouter()

router.include_router(course.router)
router.include_router(assignment.router)
router.include_router(forum.router)