from fastapi import FastAPI
from app.routers.user import user
from app.routers.auth import auth
from app.routers import instructor

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(instructor.router)
