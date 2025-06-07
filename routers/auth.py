from fastapi import APIRouter
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

class userRequest(BaseModel):
    email: str
    username : str
    first_name: str
    last_name: str
    password: str
    role: str



@router.post("/auth")
async def create_user(create_user: userRequest):
    create_user_model = Users(
        email= create_user.email,
        username = create_user.username,
        first_name= create_user.first_name,
        last_name= create_user.last_name,
        hashed_password= bcrypt_context.hash(create_user.password),
        role= create_user.role,
        is_active= True
    )
    return create_user_model