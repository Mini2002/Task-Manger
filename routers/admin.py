from fastapi import APIRouter, Depends,HTTPException,Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from database import engine, SessionLocal
from starlette import status
from pydantic import BaseModel,Field
from .auth import get_current_user


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=404, detail='Authentication failed')
    return db.query(Todos).all()
