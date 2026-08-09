from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
import uuid

from app.core.db import engine
from app.core.config import settings
from app.core import security
from app.models import User, TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"login/access-token"
)

def get_db():
    with Session(engine) as session:
        yield session

SessionDep= Annotated[Session, Depends(get_db)]
TokenDep= Annotated[str, Depends(reusable_oauth2)]

def get_current_user(session:SessionDep, token:TokenDep):
    try:
        payload= jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data= TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Couldnt validate credentials")
    user= session.get(User, uuid.UUID(token_data.sub))
    if not user:
        raise HTTPException(404, "User not found")
    if not user.is_active:
        raise HTTPException(400, "Inactive user")
    return user

CurrentUser= Annotated[User, Depends(get_current_user)]

def get_current_superuser(user: CurrentUser):
    if not user.is_superuser:
        return HTTPException(403, "User Doesnt have access")
    return user