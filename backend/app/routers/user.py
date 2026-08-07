from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, col
import uuid

from ._deps import SessionDep
from app.models import User, UserCreate, UserResponse, UserUpdate, Message
from app.core.security import get_password_hash

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

@router.get("/", response_model=list[UserResponse])
def get_users(session:SessionDep, skip:int= 0, limit:int= 10):
    statement= (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    user= session.exec(statement).all()
    return user

@router.post("/", response_model= UserResponse)
def create_user(session:SessionDep, user_in:UserCreate):
    statement= select(User).where(User.email == user_in.email)
    user= session.exec(statement).first()
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

@router.patch("/{id}", response_model= UserResponse)
def update_user(session:SessionDep, id:uuid.UUID, user_in:UserUpdate):
    user= session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")

    if user_in.email:
        statement= select(User).where(User.email == user_in.email)
        existing_user= session.exec(statement).first()
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

@router.delete("/{id}", response_model= Message)
def delete_user(session:SessionDep, id:uuid.UUID):
    user= session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")
    session.delete(user)
    session.commit()
    return Message(message= "User deleted Succesfully")