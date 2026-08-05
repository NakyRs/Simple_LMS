from fastapi import APIRouter, HTTPException

from app.models import Module, Course, ModuleResponse, ModuleCreate, ModuleUpdate, ModuleDetail, Message
from app.core.db import engine
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

router= APIRouter(
    prefix="/module",
    tags=["Module"]
)

@router.get("/", response_model= list[ModuleResponse])
def get_module():
    with Session(engine) as session:
        statement=(
            select(Module).options(selectinload(Module.lessons))
        )
        module= session.exec(statement).all()
        if not module:
            raise HTTPException(400, "Module Tidak ditemukan")
        return module

@router.post("/", response_model= ModuleResponse)
def create_module(data:ModuleCreate):
    with Session(engine) as session:
        course= session.get(Course, data.course_id)
        if not course:
            raise HTTPException(400, "Relasi Course tidak ditemukan")

        module= Module.model_validate(data)
        session.add(module)
        session.commit()
        session.refresh(module)
    return module

@router.get("/{id}", response_model= ModuleDetail)
def get_module_detail(id:int):
    with Session(engine) as session:
        statement=(
            select(Module).where(Module.id==id).options(selectinload(Module.lessons))
        )
        module= session.exec(statement).first()
        if not module:
            raise HTTPException(400, "Module Tidak ditemukan")
        return module


@router.put("/{id}", response_model= ModuleResponse)
def update_module(id:int, data:ModuleUpdate):
    with Session(engine) as session:
        module= session.get(Module,id)
        if not module:
            raise HTTPException(400, "Module tidak ditemukan")
        data_module= data.model_dump(exclude_unset=True)
        module.sqlmodel_update(data_module)
        session.add(module)
        session.commit()
        session.refresh(module)
        return module

@router.delete("/{id}", response_model= Message)
def delete_module(id:int):
    with Session(engine) as session:
        module= session.get(Module, id)
        if not module:
            raise HTTPException(400, "Module tidak ditemukan")
        session.delete(module)
        session.commit()
        return Message(message="Module Berhasil dihapus")