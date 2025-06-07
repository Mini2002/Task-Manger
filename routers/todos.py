from fastapi import APIRouter, Depends,HTTPException,Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from database import engine, SessionLocal
from starlette import status
from pydantic import BaseModel,Field


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class todoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3)
    priority: int
    complete: bool

@router.get('/')
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id:int= Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail='todo not found')

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: todoRequest):
    todo_model = Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()



