from typing import Annotated
from fastapi import APIRouter, Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'f774ab9d0b511bdb7156ed174539e7300daadf9f4d75a6a8a59ba4a7a458d1b6'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class userRequest(BaseModel):
    email: str
    username : str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str , password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta = timedelta(minutes=20)):
    encode = {"sub": username, "id": user_id, role:"role", "exp": datetime.utcnow() + expires_delta}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        username:str = payload.get('sub')
        user_id: str = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Unauthorized user') 
        return {'username':username,'user_id':user_id, 'useer_role':user_role}
    except JWTError:
         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Unauthorized user')

        

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, create_user: userRequest):
    create_user_model = Users(
        email= create_user.email,
        username = create_user.username,
        first_name= create_user.first_name,
        last_name= create_user.last_name,
        hashed_password= bcrypt_context.hash(create_user.password),
        role= create_user.role,
        is_active= True
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token")
async def login_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                      db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Unauthorized user')
    token = create_access_token(user.username, user.id, user.role)

    return {"access_token": token, "token_type": "bearer"}

    