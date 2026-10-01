from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.routers.deps import SessionDep, CurrentUser, required_role
from app.models import User, Course, Section, Lesson, CourseResponse, CoursesResponse, CourseCreate, CourseDetail, CourseUpdate, Message, Role

router= APIRouter(
    prefix="/course",
    tags=["Course"]
)

@router.get("/", dependencies= [required_role(Role.INSTRUCTOR)], response_model= CoursesResponse)
def get_course(session:SessionDep, current_user:CurrentUser):
    statement = (
        select(Course)
        .where(Course.instructor_id == current_user.id)
        .options(selectinload(Course.sections))
    )

    courses = session.exec(statement).all()

    return {
        "data": courses
    }

@router.post("/", dependencies= [required_role(Role.INSTRUCTOR)])
def create_course(session:SessionDep, current_user:CurrentUser, course_in:CourseCreate):
    course = Course(
        **course_in.model_dump(),
        instructor_id= current_user.id
    )

    session.add(course)
    session.commit()
    session.refresh(course)

    return {
        "message": "Course Created",
        "data": course
    }

@router.get("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model=CourseDetail)
def get_course_detail(session:SessionDep, current_user:CurrentUser, id:int):
    statement = (
        select(Course)
        .where(
            Course.id == id,
            Course.instructor_id == current_user.id
        )
        .options(
            selectinload(Course.sections)
            .selectinload(Section.lessons)
        )
    )
    course = session.exec(statement).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    return course

@router.put("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model= CourseResponse)
def update_course(session:SessionDep, current_user:CurrentUser, id:int, course_in:CourseUpdate):
    course = session.get(Course, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    update_dict = course_in.model_dump(exclude_unset=True)
    course.sqlmodel_update(update_dict)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course

@router.delete("/{id}", dependencies= [required_role(Role.INSTRUCTOR)], response_model=Message)
def delete(session:SessionDep, current_user:CurrentUser, id: int):
    course = session.get(Course, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not Instructor in this course")
    session.delete(course)
    session.commit()
    return Message(message="Item deleted successfully")