from fastapi import FastAPI

from app.routers import auth, user, admin, instructor, student

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(instructor.router)
app.include_router(student.router)
