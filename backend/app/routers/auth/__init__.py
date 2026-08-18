from fastapi import APIRouter
from app.routers.auth import auth 

router= APIRouter()

router.include_router(auth.router)