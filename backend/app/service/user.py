from sqlmodel import Session, select

from app.models import User


def get_user_by_email(session:Session, email:str):
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user