from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload

from app.routers.deps import SessionDep, CurrentUser, required_role
from app.models import Lesson, Section, LessonCreate, LessonUpdate, LessonResponse, LessonType, Assignment, Forum, Message, Role

router= APIRouter(
    prefix="/lesson",
    tags=["Lesson"]
)

@router.get("/", dependencies= [required_role(Role.INSTRUCTOR)], response_model= list[LessonResponse])
def get_lessons(session:SessionDep, current_user:CurrentUser,):
    statement= (
        select(Lesson)
    )
    lesson= session.exec(statement).all()
    return lesson

@router.post("/", dependencies= [required_role(Role.INSTRUCTOR)], response_model= LessonResponse)
def create_lesson(session:SessionDep, current_user:CurrentUser, data: LessonCreate):
    section= session.get(Section, data.section_id)
    if not section:
        raise HTTPException(400, "Section not found")
    if section.course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    lesson= Lesson.model_validate(data)

    if data.lesson_type == LessonType.ASSIGNMENT:
        if data.deadline is None:
            raise HTTPException(400, "Deadline required for assignment")
        lesson.assignment= Assignment()
    
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    return {
        "message": "Lesson Created",
        "data":lesson
    }

@router.get("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model= LessonResponse)
def get_detail_lesson(session:SessionDep, current_user:CurrentUser, id:int):
    statement= (
        select(Lesson).
        where(
            Lesson.id == id,
            Lesson.section.course.instructor_id == current_user.id
        )
    )
    lesson= session.exec(statement).first()
    if not lesson:
        raise HTTPException(400, "Section tidak not found")
    return lesson

@router.put("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model=LessonResponse)
def update_lesson(session:SessionDep, current_user:CurrentUser, id:int, data:LessonUpdate):
    lesson= session.get(Lesson, id)
    if not lesson:
        raise HTTPException(400, "Section not found")
    if lesson.section.course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    
    data_update= data.model_dump(exclude_unset=True)
    lesson.sqlmodel_update(data_update)
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    return lesson

@router.delete("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model= Message)
def delete_lesson(session:SessionDep, current_user:CurrentUser, id:int):
    lesson= session.get(Lesson, id)
    if not lesson:
        raise HTTPException(400, "Lesson not found")
    if lesson.section.course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    session.delete(lesson)
    session.commit()
    return Message(message="Lesson deleted successfully")