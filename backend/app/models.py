# from __future__ import annotations
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import DateTime, UniqueConstraint
from typing import Optional
import uuid
from datetime import UTC, datetime
from enum import Enum

def get_datetime_utc() -> datetime:
    return datetime.now(UTC)

class Role(str, Enum):
    STUDENT= "student"
    INSTRUCTOR= "instructor"
    ADMIN= "admin"

class LessonType(str, Enum):
    QUIZ= "quiz"
    LINK= "link"
    RESOURCE= "resource"
    ASSIGNMENT= "assignment"
    FORUM= "forum"

class EnrollmentStatus(str, Enum):
    ACTIVE= "active"
    DROPPED= "dropped"
    PAUSED= "paused"

class ForumType(str, Enum):
    TOPIC= "topic"
    REPLY= "reply"

class UserBase(SQLModel):
    name: str|None= None
    email: EmailStr= Field(index=True, unique=True)
    is_active: bool = True
    is_superuser: bool = False

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
    password: str|None= None
    role: Role|None= None
    
class UserResponse(UserBase):
    id:  uuid.UUID
    role: Role
    created_at: datetime|None= None

# Database Model
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    role: Role= Field(default= Role.STUDENT)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    courses: list["Course"]= Relationship(back_populates= "instructor")

class UserUpdateMe(SQLModel):
    name: str | None = None
    email: EmailStr | None = None

class UpdatePassword(SQLModel):
    password: str= Field(min_length=8, max_length=128)
    new_password: str= Field(min_length=8, max_length=128)

class CourseBase(SQLModel):
    title: str
    description: str | None= None

# Database Model
class Course(CourseBase, table=True):
    __tablename__ = "course"
    id: int | None = Field(default=None, primary_key=True)
    instructor_id: uuid.UUID|None= Field(foreign_key="users.id")
    instructor: User|None= Relationship(back_populates= "courses")
    sections: list["Section"] = Relationship(back_populates="course", cascade_delete=True)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(SQLModel):
    title: str|None= None
    description: str | None= None


class SectionBase(SQLModel):
    title: str
    description: str|None= None

class Section(SectionBase, table=True):
    __tablename__ = "section"
    id: int|None= Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", ondelete="CASCADE")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
    )

    course: Course|None= Relationship(back_populates="sections")
    lessons: list["Lesson"] = Relationship(back_populates="section", cascade_delete=True)

class SectionCreate(SectionBase):
    course_id: int

class SectionUpdate(SQLModel):
    title: str | None = None
    description: str | None = None


class LessonBase(SQLModel):
    title: str
    content: str|None= None

class Lesson(LessonBase, table=True):
    __tablename__ = "lesson"
    id: int|None= Field(default=None, primary_key=True)
    section_id: int = Field(foreign_key="section.id", ondelete="CASCADE")
    lesson_type: LessonType
    deadline: datetime= Field(sa_type= DateTime(timezone=True))
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
    )

    section: Section|None= Relationship(back_populates="lessons")
    assignment: Optional["Assignment"]= Relationship(back_populates="lesson")
    forum: Optional["Forum"]= Relationship(back_populates="lesson")

class LessonCreate(LessonBase):
    section_id: int
    lesson_type: LessonType
    deadline: datetime|None= None

class LessonUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    lesson_type: LessonType|None= None

class LessonProgress(SQLModel, table=True):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "lesson_id",
            name="uq_lesson_progress_user_lesson",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    lesson_id: int = Field(foreign_key="lesson.id", ondelete="CASCADE", index=True,)
    completed: bool = False
    completed_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )

class LessonProgressUpdate(SQLModel):
    completed: bool

class Assignment(SQLModel, table=True):
    __tablename__= "assignment"

    id: int|None= Field(default=None, primary_key=True)
    lesson_id: int= Field(foreign_key="lesson.id", unique=True)

    lesson: Lesson= Relationship(back_populates="assignment")
    submissions: list["Submission"]= Relationship(back_populates="assignment")

class Submission(SQLModel, table=True):
    __tablename__= "submission"
    __table_args__= (
        UniqueConstraint(
            "user_id",
            "assignment_id",
            name= "uq_submission_user_assignment"
        ),
    )
    id: int|None= Field(default=None, primary_key=True)
    user_id: uuid.UUID= Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    assignment_id: int= Field(foreign_key="assignment.id")
    created_at: datetime|None= Field(
        default_factory=get_datetime_utc,
        sa_type= DateTime(timezone=True),
    )

    assignment: Assignment= Relationship(back_populates="submissions")
    files: list["SubmissionFile"] = Relationship(
        back_populates="submission",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        },
    )

class SubmissionFile(SQLModel, table=True):
    __tablename__ = "submission_file"

    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submission.id", ondelete="CASCADE", index=True)
    original_filename: str
    storage_key: str
    mime_type: str | None = None
    size: int | None = None
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
    )

    submission: Submission = Relationship(back_populates= "files")

class Forum(SQLModel, table=True):
    __tablename__= "forum"

    id: int|None= Field(default=None, primary_key=True)
    lesson_id: int|None= Field(default=None, foreign_key="lesson.id", index=True)
    parent_id: int|None= Field(default=None, foreign_key="forum.id")
    user_id: uuid.UUID= Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    title: str|None= Field(default=None)
    content: str|None= Field(default=None)
    reply_level: int= Field(default=0, ge=0, le=3)
    post_type: ForumType
    created_at: datetime|None= Field(
        default_factory= get_datetime_utc,
        sa_type= DateTime(timezone=True)
    )

    lesson: Lesson= Relationship(back_populates="forum")
    parent: Optional["Forum"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={
            "remote_side": "Forum.id"
        }
    )

    replies: list["Forum"] = Relationship(
        back_populates="parent"
    )

class ForumCreate(SQLModel):
    lesson_id: int|None
    parent_id: int|None
    title: str|None
    content: str|None
    post_type: ForumType

class ForumResponse(SQLModel):
    id: int
    user_id: uuid.UUID
    title: str | None
    content: str | None
    reply_level: int
    post_type: ForumType
    created_at: datetime | None
    replies: list["ForumResponse"] = []

class Enrollment(SQLModel, table=True):
    __tablename__ = "enrollment"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            name="uq_enrollment_user_course",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE", index=True,)
    course_id: int = Field(foreign_key="course.id", ondelete="CASCADE", index=True,)
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    enrolled_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
    )

class EnrollmentCreate(SQLModel):
    user_id: uuid.UUID
    course_id: int

class EnrollmentUpdate(SQLModel):
    status: EnrollmentStatus | None = None

class SectionResponse(SectionBase):
    id: int

class LessonResponse(LessonBase):
    id: int
    lesson_type: LessonType

class CourseResponse(CourseBase):
    id: int


class SectionDetail(SectionResponse):
    lessons: list[LessonResponse] = Field(default_factory=list)

class CourseDetail(CourseResponse):
    sections: list[SectionDetail] = Field(default_factory=list)


class CoursesResponse(SQLModel):
    data: list[CourseResponse]


class Message(SQLModel):
    message: str

class Token(SQLModel):
    access_token: str
    token_type: str= "bearer"

class TokenPayload(SQLModel):
    sub: str|None= None