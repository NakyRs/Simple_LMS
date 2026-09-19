from sqlmodel import Session, select, create_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, UserCreate

connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=True,
)

def init_db(session:Session):
    user= session.exec(
        select(User)
        .where(
            User.email==settings.FIRST_SUPERUSER
        )
    ).first()
    if not user:
        user_in= UserCreate(
            email= settings.FIRST_SUPERUSER,
            password= settings.FIRST_SUPERUSER_PASSWORD,
            is_active= True,
            is_superuser= True
        )
        user= User.model_validate(user_in, update={"hashed_password": get_password_hash(user_in.password)})
        session.add(user)
        session.commit()