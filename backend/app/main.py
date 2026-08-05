from fastapi import FastAPI
from app.routers import course, module, lesson

app = FastAPI()

app.include_router(course.router)
app.include_router(module.router)
app.include_router(lesson.router)
