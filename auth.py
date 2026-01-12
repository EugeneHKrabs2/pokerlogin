from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from database import DynamoDB


load_dotenv()

router = APIRouter(
    prefix = '/auth',
    tags = ['auth']
)

SECRET_KEY = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ISSUER = "https://auth.myapp.com"
AUDIENCE = "my-api"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

users = DynamoDB()

class CreateUserRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI()

def verify_password(plain, hashed):
    return bcrypt_context.verify(plain, hashed)

def create_access_token(data: dict):
    now = datetime.utcnow()
    payload = {
        **data,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

@app.post("/auth/login")
def login(email: str, password: str):
    user = users.get_user(email) #change this to actual database
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"],
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

@app.post("/auth/register")
def register(user: CreateUserRequest):
    hashed_password = bcrypt_context.hash(user.password)
    if not users.create_user(user.email, hashed_password):
        raise HTTPException(status_code=400, detail="User already exists")

    return {"message": "User created successfully"}