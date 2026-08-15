from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, col
import uuid
from typing import Annotated

from app.routers.deps import SessionDep, CurrentUser, get_current_superuser
from app.service import user as user_service
from app.models import User, UserCreate, UserResponse, UserUpdate, UserRegister, UserUpdateMe, UpdatePassword, Message
from app.core.security import get_password_hash, verify_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

users_db=[
    {
        "name": "jokowi",
        "email": "joko@gmail.com"
    },
]

@router.get("/me", response_model= UserResponse)
def get_user_me(current_user: CurrentUser):
    return current_user

@router.patch("/me", response_model= UserResponse)
def update_user_me(session:SessionDep, current_user:CurrentUser, user_in: UserUpdateMe):
    if user_in.email:
        existing_user= user_service.get_user_by_email(session, user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(409, "User already exist")

    update_dict= user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(update_dict)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@router.patch("/me/password", response_model= Message)
def update_password_me(session:SessionDep, current_user:CurrentUser, password_in:UpdatePassword):
    verified, _= verify_password(password_in.password, current_user.hashed_password)
    if not verified:
        raise HTTPException(400, "Wrong password")
    if password_in.password == password_in.new_password:
        raise HTTPException(400, "new password must be different with the current password")
    new_hash_password= get_password_hash(password_in.new_password)
    current_user.hashed_password= new_hash_password
    session.add(current_user)
    session.commit()
    return Message(message="Password Updated")

@router.delete("/me",response_model= Message)
def delete_user_me(session:SessionDep, current_user:CurrentUser):
    if current_user.is_superuser:
        raise HTTPException(403, "Super user not allowed to delete themselves")
    session.delete(current_user)
    session.commit()
    return Message(message= "User deleted Succesfully")

@router.get("/", dependencies= [Depends(get_current_superuser)], response_model=list[UserResponse])
def get_users(session:SessionDep, skip:int= 0, limit:int= 10):
    statement= (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    user= session.exec(statement).all()
    return user

@router.post("/", dependencies= [Depends(get_current_superuser)], response_model= UserResponse)
def create_user(session:SessionDep, user_in:UserCreate):
    user= user_service.get_user_by_email(session, user_in.email)
    if user:
        raise HTTPException(400, "User already exist")
    user= User.model_validate(user_in, update={"hashed_password": get_password_hash(user_in.password)})
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/{id}", response_model= UserResponse)
def get_user_detail(session:SessionDep, id:uuid.UUID):
    user= session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.patch("/{id}", dependencies= [Depends(get_current_superuser)], response_model= UserResponse)
def update_user(session:SessionDep, id:uuid.UUID, user_in:UserUpdate):
    user= session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")

    if user_in.email:
        existing_user= user_service.get_user_by_email(session, user_in.email)
        if existing_user and existing_user.id != id:
            raise HTTPException(409, "User already exist")
        
    update_dict= user_in.model_dump(exclude_unset=True)
    extra_data={}
    if "password" in update_dict:
        password = update_dict["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password

    user.sqlmodel_update(update_dict, update=extra_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user 

@router.delete("/{id}", dependencies= [Depends(get_current_superuser)],response_model= Message)
def delete_user(session:SessionDep, current_user:CurrentUser, id:uuid.UUID):
    user= session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")
    if user == current_user:
        raise HTTPException(403, "Super user not allowed to delete themselves")
    session.delete(user)
    session.commit()
    return Message(message= "User deleted Succesfully")
