from fastapi import APIRouter, HTTPException

from app.core.db import engine
from app.models import Lesson, Section, LessonCreate, LessonUpdate, LessonResponse, Message
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload

router= APIRouter(
    prefix="/lesson",
    tags=["Lesson"]
)

@router.get("/", response_model= list[LessonResponse])
def get_lessons():
    with Session(engine) as session:
        statement= (
            select(Lesson)
        )
        lesson= session.exec(statement).all()
        return lesson

@router.post("/", response_model= LessonResponse)
def create_lesson(data: LessonCreate):
    with Session(engine) as session:
        section= session.get(Section, data.section_id)
        if not section:
            raise HTTPException(400, "relasi section tidak ditemukan")
        lesson= Lesson.model_validate(data)
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        return lesson

@router.get("/{id}", response_model= LessonResponse)
def get_detail_lesson(id:int):
    with Session(engine) as session:
        statement= (
            select(Lesson).
            where(Lesson.id == id)
        )
        lesson= session.exec(statement).first()
        if not lesson:
            raise HTTPException(400, "Relasi Section tidak ditemukan")
        return lesson

@router.put("/{id}", response_model=LessonResponse)
def update_lesson(id:int, data:LessonUpdate):
    with Session(engine) as session:
        lesson= session.get(Lesson, id)
        if not lesson:
            raise HTTPException(400, "Relasi Section tidak ditemukan")
        data_update= data.model_dump(exclude_unset=True)
        lesson.sqlmodel_update(data_update)
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        return lesson

@router.delete("/{id}", response_model= Message)
def delete_lesson(id:int):
    with Session(engine) as session:
        lesson= session.get(Lesson, id)
        if not lesson:
            raise HTTPException(400, "Lesson tidak ditemukan")
        session.delete(lesson)
        session.commit()
        return Message(message="Lesson berhasil dihapus")