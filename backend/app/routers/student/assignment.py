# routers/submission.py

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.routers.deps import SessionDep, CurrentUser, required_role
from app.service.utils import save_upload_file
from app.models import Role, EnrollmentStatus, Assignment, Submission, SubmissionFile, Enrollment

router = APIRouter(
    prefix="/assignment",
    tags=["Assignment"],
)

BASE_DIR= Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "storage" / "submissions"
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

@router.get("/{lesson_id}")
def get_assignment(
    lesson_id: int,
    session: SessionDep,
    current_user: CurrentUser
):
    assignment= session.exec(
        select(Assignment)
        .where(
            Assignment.lesson_id == lesson_id
        )
    ).first()
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    
    course_id= assignment.lesson.section.course_id
    enrollment= session.exec(
        select(Enrollment)
        .where(
            Enrollment.user_id == current_user.id,
            Enrollment.status== EnrollmentStatus.ACTIVE,
            Enrollment.course_id==course_id
        )
    ).first()
    if not enrollment:
        raise HTTPException(403, "You are not enrolled in this course")
    
    submission = session.exec(
        select(Submission)
        .where(
            Submission.assignment_id == assignment.id,
            Submission.user_id == current_user.id,
        )
    ).first()

    return {
        "lesson_id": assignment.lesson_id,
        "deadline": assignment.deadline,
        "assignment": {
            "id": submission.id,
            "files": [file.id for file in submission.files]
        }
    }

@router.post("/{assignment_id}/submission", dependencies= Depends(required_role(Role.STUDENT)))
async def create_submission(
    session: SessionDep,
    current_user: CurrentUser,
    assignment_id: int,
    files: list[UploadFile] = File(...),
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")

    course_id= assignment.lesson.section.course_id
    enrollment= session.exec(
        select(Enrollment)
        .where(
            Enrollment.user_id == current_user.id,
            Enrollment.status== EnrollmentStatus.ACTIVE,
            Enrollment.course_id==course_id
        )
    ).first()
    if not enrollment:
        raise HTTPException(403, "You are not enrolled in this course")
    
    submission = Submission(
        user_id= current_user.id,
        assignment_id= assignment_id,
    )

    session.add(submission)
    session.commit()
    session.refresh(submission)

    for file in files:
        file_extension = (
            Path(file.filename).suffix
            if file.filename
            else ""
        )

        generated_name= f"{uuid.uuid4()}{file_extension}"
        submission_dir= UPLOAD_DIR / str(submission.id)
        submission_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path= submission_dir / generated_name

        content= await save_upload_file(
            file,
            file_path,
        )

        submission_file = SubmissionFile(
            submission_id=submission.id,
            original_filename=file.filename or generated_name,
            storage_key=str(file_path),
            mime_type=file.content_type,
            size=content,
        )

        session.add(submission_file)

    session.commit()

    return {
        "message": "Submission created",
        "submission_id": submission.id,
    }

@router.get("/submission/files/{file_id}")
def download_file(
    file_id: int,
    session: SessionDep,
    current_user: CurrentUser
):
    submission_file = session.get(
        SubmissionFile,
        file_id,
    )
    if not submission_file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
    )
    
    if submission_file.submission.user_id != current_user.id:
        raise HTTPException(403, "User doesnt have access")
    

    file_path = Path(
        submission_file.storage_key
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return FileResponse(
        path=file_path,
        filename=submission_file.original_filename,
        media_type=submission_file.mime_type,
    )