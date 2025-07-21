from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from . import models
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ..local_exceptions import AuthenticationError
import logging
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password: str , hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)

def authenticate_user(email: str, password: str, db: Session) -> str | None:
    TEMP_ADMIN_EMAIL = os.getenv("TEMP_ADMIN_EMAIL")
    TEMP_ADMIN_PASSWORD = os.getenv("TEMP_ADMIN_PASSWORD")
    
    if email == TEMP_ADMIN_EMAIL and password == TEMP_ADMIN_PASSWORD:
        return email
    
    logging.warning(f"Failed authentication attempt for email: {email}")
    return None

def create_access_token(email: str, expires_delta: timedelta) -> str:
    encode = {
        'sub': email,
        'exp': datetime.now(timezone.utc) + expires_delta
    }

    logging.info(f"Creating access token for email: {email} with expiration: {expires_delta}")
    if not SECRET_KEY:  
        raise ValueError("SECRET_KEY environment variable is not set.")
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> models.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('id')
        return models.TokenData(user_id=user_id)
    except PyJWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise AuthenticationError()

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> models.TokenData:
    return verify_token(token)

CurrentUser = Annotated[models.TokenData, Depends(get_current_user)]

def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Session) -> models.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthenticationError()
    token = create_access_token(user, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return models.Token(access_token=token, token_type='bearer')
