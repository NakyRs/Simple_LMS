from fastapi import APIRouter, HTTPException

from app.models import Section, Course, SectionResponse, SectionCreate, SectionUpdate, SectionDetail, Message
from app.core.db import engine
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

router= APIRouter(
    prefix="/section",
    tags=["Section"]
)

@router.get("/", response_model= list[SectionResponse])
def get_section():
    with Session(engine) as session:
        statement=(
            select(Section).options(selectinload(Section.lessons))
        )
        section= session.exec(statement).all()
        if not section:
            raise HTTPException(400, "Section Tidak ditemukan")
        return section

@router.post("/", response_model= SectionResponse)
def create_section(data:SectionCreate):
    with Session(engine) as session:
        course= session.get(Course, data.course_id)
        if not course:
            raise HTTPException(400, "Relasi Course tidak ditemukan")

        section= Section.model_validate(data)
        session.add(section)
        session.commit()
        session.refresh(section)
    return section

@router.get("/{id}", response_model= SectionDetail)
def get_section_detail(id:int):
    with Session(engine) as session:
        statement=(
            select(Section).where(Section.id==id).options(selectinload(Section.lessons))
        )
        section= session.exec(statement).first()
        if not section:
            raise HTTPException(400, "Section Tidak ditemukan")
        return section


@router.put("/{id}", response_model= SectionResponse)
def update_section(id:int, data:SectionUpdate):
    with Session(engine) as session:
        section= session.get(Section,id)
        if not section:
            raise HTTPException(400, "Section tidak ditemukan")
        data_Section= data.model_dump(exclude_unset=True)
        section.sqlmodel_update(data_Section)
        session.add(section)
        session.commit()
        session.refresh(section)
        return section

@router.delete("/{id}", response_model= Message)
def delete_section(id:int):
    with Session(engine) as session:
        section= session.get(Section, id)
        if not section:
            raise HTTPException(400, "Section tidak ditemukan")
        session.delete(section)
        session.commit()
        return Message(message="Section Berhasil dihapus")