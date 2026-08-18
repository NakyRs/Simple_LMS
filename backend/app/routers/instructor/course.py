from fastapi import APIRouter, HTTPException
from app.models import User, Course, Section, Lesson, CourseResponse, CoursesResponse, CourseCreate, CourseDetail, CourseUpdate, Message, Role
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.core.db import engine

router= APIRouter(
    prefix="/course",
    tags=["Course"]
)

course_db = [
    {
        "id": 1,
        "title": "Belajar Python",
        "description": "Dasar Python",
        "code_course": "PY001",
    },
    {
        "id": 2,
        "title": "FastAPI",
        "description": "REST API dengan FastAPI",
        "code_course": "API001",
    }
]
@router.get("/", response_model= CoursesResponse)
def get_course():
    with Session(engine) as session:
        statement = (
            select(Course)
            .options(selectinload(Course.sections))
        )

        courses = session.exec(statement).all()

        return {
            "data": courses
        }

@router.post("/")
def create_course(course_in:CourseCreate):
    # course_in["id"]= max((item["id"] for item in course_db), default=0)+1
    # new_course = {
    #     "id": max((item["id"] for item in course_db), default=0) + 1,
    #     **course_in.model_dump()
    # }
    # course_db.append(new_course)
    with Session(engine) as session:
        user= session.get(User, course_in.instructor_id)
        if not user:
            raise HTTPException(404, "User not found")
        if user.role not in [Role.INSTRUCTOR, Role.ADMIN]:
            raise HTTPException(409, "Role bukan instructor")
        course = Course.model_validate(course_in)

        session.add(course)
        session.commit()
        session.refresh(course)

        print(course.id)
        return {
            "message": "Course berhasil dibuat",
            "data": course
        }

@router.get("/{id}", response_model=CourseDetail)
def get_course_detail(id:int):
    # for i in course_db:
    #     if i["id"]==id:
    #         return i 
    with Session(engine) as session:
        statement = (
            select(Course)
            .where(Course.id == id)
            .options(
                selectinload(Course.sections)
                .selectinload(Section.lessons)
            )
        )

        course = session.exec(statement).first()

        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        return course

@router.put("/{id}", response_model= CourseResponse)
def update_course(id:int, course_in:CourseUpdate):
    # for course in course_db:
    #     if course["id"] == id:
    #         # Update hanya field yang dikirim
    #         update_data = course_in.model_dump(exclude_unset=True)
    #         course.update(update_data)
    #         return course
    with Session(engine) as session:
        course = session.get(Course, id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        update_dict = course_in.model_dump(exclude_unset=True)
        course.sqlmodel_update(update_dict)
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

@router.delete("/{id}", response_model=Message)
def delete(id: int):
    # for index, course in enumerate(course_db):
    #     if course["id"] == id:
    #         return course_db.pop(index)
    with Session(engine) as session:
        course = session.get(Course, id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        session.delete(course)
        session.commit()
        return Message(message="Item deleted successfully")



# from sqlmodel import Session, select

# from app.models import Course


# class CourseRepository:

#     def create(self, session: Session, data: Course):
#         session.add(data)
#         session.commit()
#         session.refresh(data)
#         return data

#     def get_all(self, session: Session):
#         return session.exec(select(Course)).all()

#     def get_by_id(self, session: Session, course_id: int):
#         return session.get(Course, course_id)

#     def update(self, session: Session, course: Course):
#         session.commit()
#         session.refresh(course)
#         return course

#     def delete(self, session: Session, course: Course):
        # session.delete(course)
        # session.commit()