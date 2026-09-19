from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.routers.deps import SessionDep, CurrentUser, required_role
from app.service.utils import forum_to_response
from app.models import Role, Course, Section, Lesson, Forum, ForumType, ForumCreate, ForumResponse, Enrollment, EnrollmentStatus


router= APIRouter(
    prefix="/forum",
    tags=["Student-Forum"]
)

@router.get("/topic/{lesson_id}", dependencies= [Depends(required_role(Role.STUDENT))])
def get_forum_detail(session:SessionDep, current_user:CurrentUser, lesson_id:int):
    lesson= session.get(Lesson, lesson_id)
    enrollment= session.exec(
        select(Enrollment)
        .where(
            Enrollment.user_id == current_user.id,
            Enrollment.status== EnrollmentStatus.ACTIVE,
            Enrollment.course_id== lesson.section.course_id
        )
    ).first()
    if not enrollment:
        raise HTTPException(403, "You are not enrolled in this course")
    if not lesson:
        raise HTTPException(404, "lesson not found")
    
    forum= session.exec(
        select(Forum)
        .where(
            Forum.lesson_id==lesson_id,
            Forum.post_type==ForumType.TOPIC
        )
    ).all()
    if not forum:
        raise HTTPException(404, "forum not found")
    
    return {
        "course_id": lesson.section.course_id,
        "title": lesson.title,
        "content": lesson.content,
        "topics": forum
    }

@router.get("/reply/{forum_id}", dependencies= [Depends(required_role(Role.STUDENT))])
def get_topic_reply(session:SessionDep, current_user:CurrentUser, forum_id:int):
    forum= session.get(Forum, forum_id)
    enrollment= session.exec(
        select(Enrollment)
        .where(
            Enrollment.user_id == current_user.id,
            Enrollment.status== EnrollmentStatus.ACTIVE,
            Enrollment.course_id== forum.lesson.section.course_id
        )
    ).first()
    if not enrollment:
        raise HTTPException(403, "You are not enrolled in this course")
    
    if not forum:
        raise HTTPException(404, "Topic not found")
    if forum.post_type != ForumType.TOPIC:
        raise HTTPException(400, "Forum id must reference a topic")
    
    forums= session.exec(
        select(Forum)
        .where(
            Forum.post_type==ForumType.REPLY,
            Forum.id==forum.id
        )
        .options(
            selectinload(Forum.replies)
            .selectinload(Forum.replies)
            .selectinload(Forum.replies)
        )
    ).one_or_none()

    return forum_to_response(forums)

@router.post("/reply/{forum_id}", dependencies= [Depends(required_role(Role.STUDENT))])
def create_reply(session:SessionDep, current_user:CurrentUser, forum_id:int, data:ForumCreate):
    forum= session.get(Forum, forum_id)
    enrollment= session.exec(
        select(Enrollment)
        .where(
            Enrollment.user_id == current_user.id,
            Enrollment.status== EnrollmentStatus.ACTIVE,
            Enrollment.course_id== forum.lesson.section.course_id
        )
    ).first()
    if not enrollment:
        raise HTTPException(403, "You are not enrolled in this course")
    if not forum:
        raise HTTPException(404, "Forum not found")

    reply= Forum(
        lesson_id= forum.lesson_id,
        parent_id= forum.id,
        user_id= current_user.id,
        title= data.title,
        content= data.content,
        reply_level= forum.reply_level+1,
        post_type= ForumType.REPLY
    )
    session.add(reply)
    session.commit()

    return{
        "message": "reply created"
    }