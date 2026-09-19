from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.routers.deps import SessionDep, CurrentUser, required_role
from app.service.utils import forum_to_response
from app.models import Role, Course, Section, Lesson, Forum, ForumType, ForumCreate, ForumResponse, Enrollment
router= APIRouter(
    prefix="/forum",
    tags=["Forum"]
)

@router.get("/topic/{lesson_id}", dependencies= [Depends(required_role(Role.INSTRUCTOR))])
def get_topics(session:SessionDep, current_user:CurrentUser, lesson_id:int):
    lesson= session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "lesson not found")
    if lesson.section.course.instructor_id != current_user.id:
        raise HTTPException(403, "You are not Instructor in this course")
    forum= session.exec(
        select(Forum)
        .where(
            Forum.lesson_id==lesson_id,
            Forum.post_type==ForumType.TOPIC
        )
    ).all()
    if not forum:
        raise HTTPException(404, "forum not found")
    return forum

@router.post("/topic/{lesson_id}", dependencies= [Depends(required_role(Role.INSTRUCTOR))])
def create_topic(session:SessionDep, current_user:CurrentUser, lesson_id:int, data:ForumCreate):
    lesson= session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "lesson not found")
    if lesson.section.course.instructor_id != current_user.id:
        raise HTTPException(403, "You are not Instructor in this course")

    forum= Forum(
        lesson_id= lesson_id,
        title= data.title,
        content= data.content,
        post_type= data.post_type
    )
    session.add(forum)
    session.commit()
    return{
        "message": "topic created"
    }

@router.get("/reply/{forum_id}", dependencies= [Depends(required_role(Role.INSTRUCTOR))])
def get_topic_reply(session:SessionDep, current_user:CurrentUser, forum_id:int):
    topic= session.get(Forum, forum_id)
    if not topic:
        raise HTTPException(404, "Topic not found")
    if topic.post_type != ForumType.TOPIC:
        raise HTTPException(400, "Forum id must reference a topic")
    if topic.lesson.section.course.instructor_id != current_user.id:
        raise HTTPException(403, "You are not Instructor in this course")
    
    forum= session.exec(
        select(Forum)
        .where(
            Forum.post_type==ForumType.REPLY,
            Forum.id==topic.id
        )
        .options(
            selectinload(Forum.replies)
            .selectinload(Forum.replies)
            .selectinload(Forum.replies)
        )
    ).one_or_none()

    return forum_to_response(forum)

@router.post("/reply/{forum_id}", dependencies= [Depends(required_role(Role.INSTRUCTOR))])
def create_reply(session:SessionDep, current_user:CurrentUser, forum_id:int, data:ForumCreate):
    forum= session.get(Forum, forum_id)
    if not forum:
        raise HTTPException(404, "Forum not found")
    if forum.lesson.section.course.instructor_id != current_user.id:
        raise HTTPException(403, "You are not Instructor in this course")

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