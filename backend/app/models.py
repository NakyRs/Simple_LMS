# from __future__ import annotations
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel
import uuid

class UserBase(SQLModel):
    name: str
    email: EmailStr= Field(index=True, unique=True)

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int

# Database Model
class User(UserBase, table=True):
    __tablename__ = "users"

    id: int|None = Field(default=None, primary_key=True)
    hashed_password: str


class CourseBase(SQLModel):
    title: str
    description: str | None
    code_course: str

# Database Model
class Course(CourseBase, table=True):
    __tablename__ = "course"
    id: int | None = Field(default=None, primary_key=True)
    modules: list["Module"] = Relationship(back_populates="course", cascade_delete=True)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(SQLModel):
    title: str|None= None
    description: str | None= None
    code_course: str|None= None


class ModuleBase(SQLModel):
    title: str
    description: str|None= None

class Module(ModuleBase, table=True):
    __tablename__ = "module"
    id: int|None= Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", ondelete="CASCADE")
    course: Course|None= Relationship(back_populates="modules")
    lessons: list["Lesson"] = Relationship(back_populates="module", cascade_delete=True)

class ModuleCreate(ModuleBase):
    course_id: int

class ModuleUpdate(SQLModel):
    title: str | None = None
    description: str | None = None


class LessonBase(SQLModel):
    title: str
    content: str|None= None

class Lesson(LessonBase, table=True):
    __tablename__ = "lesson"
    id: int|None= Field(default=None, primary_key=True)
    module_id: int = Field(foreign_key="module.id", ondelete="CASCADE")
    module: Module|None= Relationship(back_populates="lessons")

class LessonCreate(LessonBase):
    module_id: int

class LessonUpdate(SQLModel):
    title: str | None = None
    content: str | None = None


class ModuleResponse(ModuleBase):
    id: int

class LessonResponse(LessonBase):
    id: int

class CourseResponse(CourseBase):
    id: int


class ModuleDetail(ModuleResponse):
    lessons: list[LessonResponse] = Field(default_factory=list)

class CourseDetail(CourseResponse):
    modules: list[ModuleDetail] = Field(default_factory=list)


class CoursesResponse(SQLModel):
    data: list[CourseResponse]


class Message(SQLModel):
    message: str