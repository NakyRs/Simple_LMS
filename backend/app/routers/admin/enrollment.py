from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.routers.deps import CurrentUser, required_role, SessionDep
from app.models import Enrollment, Course, User, Role, EnrollmentCreate, EnrollmentUpdate, EnrollmentStatus, Message

router= APIRouter(
    prefix="/enrollment",
    tags=["Admin-Enrollment"]
    )

@router.get( "/", response_model= list[Enrollment], dependencies= [Depends(required_role(Role.ADMIN, Role.INSTRUCTOR))])
def get_enrollments(session: SessionDep):
    enrollments = session.exec(
        select(Enrollment)
    ).all()

    return enrollments

@router.get("/{enrollment_id}", response_model= Enrollment, dependencies= [Depends(required_role(Role.ADMIN, Role.INSTRUCTOR))])
def get_enrollment(session: SessionDep, enrollment_id: int):
    enrollment = session.get(Enrollment, enrollment_id)

    if not enrollment:
        raise HTTPException(404, "Enrollment not found")

    return enrollment

@router.post("/", dependencies= [Depends(required_role(Role.ADMIN, Role.INSTRUCTOR))])
def create_enrollment(session:SessionDep, enrollment_in:EnrollmentCreate):
    user = session.get(User, enrollment_in.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    course= session.get(Course, enrollment_in.course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    existing = session.exec(
        select(Enrollment).where(
            Enrollment.user_id == enrollment_in.user_id,
            Enrollment.course_id == enrollment_in.course_id,
        )
    ).first()

    if existing:
        raise HTTPException(409, "User is already enrolled in this course")

    enrollment= Enrollment.model_validate(enrollment_in)

    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)

    return enrollment

@router.patch("/{enrollment_id}", dependencies= [Depends(required_role(Role.ADMIN, Role.INSTRUCTOR))])
def update_enrollment(session:SessionDep, enrollment_id: int, enrollment_in: EnrollmentUpdate):
    enrollment = session.get(Enrollment, enrollment_id)

    if not enrollment:
        raise HTTPException(404, "Enrollment not found")

    update_data = enrollment_in.model_dump(exclude_unset=True)

    enrollment.sqlmodel_update(update_data)

    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)

    return enrollment

@router.delete("/{enrollment_id}", dependencies= [Depends(required_role(Role.ADMIN, Role.INSTRUCTOR))], response_model= Message)
def delete_enrollment(session: SessionDep, enrollment_id: int):
    enrollment= session.get(Enrollment, enrollment_id)

    if not enrollment:
        raise HTTPException(404, "Enrollment not found")

    session.delete(enrollment)
    session.commit()
    return Message(message="Enrollment deleted")