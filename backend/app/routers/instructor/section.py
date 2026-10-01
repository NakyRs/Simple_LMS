from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.routers.deps import SessionDep, CurrentUser, required_role
from app.models import Section, Course, SectionResponse, SectionCreate, SectionUpdate, SectionDetail, Message, Role

router= APIRouter(
    prefix="/section",
    tags=["Section"]
)

@router.get("/", dependencies= [required_role(Role.INSTRUCTOR)], response_model= list[SectionResponse])
def get_section(session:SessionDep, current_user:CurrentUser):
    statement=(
        select(Section)
        .where(Section.course.instructor_id == current_user.id)
        .options(selectinload(Section.lessons))
    )
    section= session.exec(statement).all()
    if not section:
        raise HTTPException(400, "Section not found")
    return section

@router.post("/", dependencies= [required_role(Role.INSTRUCTOR)])
def create_section(session:SessionDep, current_user:CurrentUser, data:SectionCreate):
    course= session.get(Course, data.course_id)
    if not course:
        raise HTTPException(400, "Course not found")
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    
    section= Section.model_validate(data)
    session.add(section)
    session.commit()
    session.refresh(section)
    return {
        "message":"Section Created",
        "data": section
    }

@router.get("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model= SectionDetail)
def get_section_detail(session:SessionDep, current_user:CurrentUser, id:int):
    statement=(
        select(Section)
        .where(
            Section.id==id,
            Section.course.instructor_id == current_user.id
        )
        .options(selectinload(Section.lessons))
    )
    section= session.exec(statement).first()
    if not section:
        raise HTTPException(400, "Section not found")
    return section


@router.put("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model= SectionResponse)
def update_section(session:SessionDep, current_user:CurrentUser, id:int, data:SectionUpdate):
    section= session.get(Section,id)
    if not section:
        raise HTTPException(400, "Section not found")
    if section.course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    
    data_Section= data.model_dump(exclude_unset=True)
    section.sqlmodel_update(data_Section)
    session.add(section)
    session.commit()
    session.refresh(section)
    return section

@router.delete("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model= Message)
def delete_section(session:SessionDep, current_user:CurrentUser, id:int):
    section= session.get(Section, id)
    if not section:
        raise HTTPException(400, "Section not found")
    if section.course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    
    session.delete(section)
    session.commit()
    return Message(message="Section deleted successfully")