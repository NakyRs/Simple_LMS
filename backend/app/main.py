from fastapi import FastAPI
from app.routers import user, course, module, lesson

app = FastAPI()

app.include_router(user.router)
app.include_router(course.router)
app.include_router(module.router)
app.include_router(lesson.router)
