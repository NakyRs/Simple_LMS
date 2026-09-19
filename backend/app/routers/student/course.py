from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.routers.deps import SessionDep, CurrentUser, required_role
from app.models import Role, EnrollmentStatus, Course, CourseDetail, Section, Enrollment, Lesson, LessonProgress, LessonProgressUpdate, get_datetime_utc

router= APIRouter(
    prefix="/course", 
    tags=["Student-course"]
    )

@router.get("/", dependencies= [Depends(required_role(Role.STUDENT))])
def get_student_courses(session:SessionDep, current_user:CurrentUser):
    statement = (
        select(Course)
        .join(Enrollment)
        .where(
            Enrollment.user_id == current_user.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
        )
    )
    return session.exec(statement).all()

@router.get("/progress", dependencies=[Depends(required_role(Role.STUDENT))])
def get_student_progress(session: SessionDep, current_user: CurrentUser):
    statement = (
        select(LessonProgress)
        .where(
            LessonProgress.user_id == current_user.id,
        )
    )

    return session.exec(statement).all()

@router.patch("/progress/{lesson_id}", dependencies=[Depends(required_role(Role.STUDENT))])
def update_student_progress(session: SessionDep, current_user: CurrentUser, lesson_id: int, progress_in: LessonProgressUpdate):
    lesson = session.get(Lesson, lesson_id)

    if not lesson:
        raise HTTPException(404, "Lesson not found")

    statement = (
        select(Enrollment)
        .join(Course, Course.id == Enrollment.course_id)
        .join(Section, Section.course_id == Course.id)
        .where(
            Enrollment.user_id == current_user.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
            Section.id == lesson.section_id,
        )
    )

    enrollment = session.exec(statement).first()

    if not enrollment:
        raise HTTPException(403, "You are not enrolled in this course")

    statement = (
        select(LessonProgress)
        .where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )

    progress = session.exec(statement).first()

    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
        )

    progress.completed = progress_in.completed

    if progress.completed:
        progress.completed_at = get_datetime_utc()
    else:
        progress.completed_at = None

    session.add(progress)
    session.commit()
    session.refresh(progress)

    return progress

@router.get("/{course_id}", dependencies=[Depends(required_role(Role.STUDENT))], response_model=CourseDetail)
def get_student_course(session: SessionDep, current_user: CurrentUser, course_id: int):
    statement = (
        select(Course)
        .join(Enrollment)
        .where(
            Course.id == course_id,
            Enrollment.user_id == current_user.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
        )
        .options(
            selectinload(Course.sections)
            .selectinload(Section.lessons)
        )
    )

    course = session.exec(statement).first()

    if not course:
        raise HTTPException(404, "Course not found")

    return course