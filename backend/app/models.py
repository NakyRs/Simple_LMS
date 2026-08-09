# from __future__ import annotations
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import DateTime
import uuid
from datetime import UTC, datetime

def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


class UserBase(SQLModel):
    name: str|None= None
    email: EmailStr= Field(index=True, unique=True)
    is_active: bool = True
    is_superuser: bool = False
    is_staff: bool = False

class UserCreate(UserBase):
    password: str

class UserRegister(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(SQLModel):
    name: str | None = None
    email: EmailStr | None = None
    is_active: bool|None = None
    is_superuser: bool|None = None
    is_staff: bool|None = None
    password: str|None= None

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    
class UserResponse(UserBase):
    id:  uuid.UUID
    created_at: datetime|None= None

# Database Model
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

class UserUpdateMe(SQLModel):
    name: str | None = None
    email: EmailStr | None = None

class UpdatePassword(SQLModel):
    password: str
    new_password: str

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

class Token(SQLModel):
    access_token: str
    token_type: str= "bearer"

class TokenPayload(SQLModel):
    sub: str|None= None