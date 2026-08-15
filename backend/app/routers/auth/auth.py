from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session
from typing import Annotated
from datetime import timedelta

from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.service import user as user_service
from app.routers.deps import SessionDep
from app.models import User, UserRegister, UserResponse, Token

router= APIRouter(
    tags=['Login']
)

DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

@router.post("/login/access-token")
def login_access_token(session:SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # statement= (select(User).where(User.email==form_data.username))
    # user= session.exec(statement).first()
    user= user_service.get_user_by_email(session, form_data.username)
    if not user:
        verify_password(form_data.password, DUMMY_HASH)
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    verified, update_password_hash= verify_password(form_data.password, user.hashed_password)
    
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if update_password_hash:
        user.hashed_password= update_password_hash
        session.add(user)
        session.commit()
        session.refresh(user)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="inactive user")
    
    access_token_exp= timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
    return Token(
        access_token= create_access_token(subject=user.id, expires_delta=access_token_exp)
    )


@router.post("/signup", response_model= UserResponse)
def register_user(session:SessionDep, user_in:UserRegister):
    user= user_service.get_user_by_email(session, user_in.email)
    if user:
        raise HTTPException(409, "Email already exist")
    user= User.model_validate(user_in, update={"hashed_password": get_password_hash(user_in.password)})
    session.add(user)
    session.commit()
    session.refresh(user)
    return user