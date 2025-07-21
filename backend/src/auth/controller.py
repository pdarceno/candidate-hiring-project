from typing import Annotated
from fastapi import APIRouter, Depends, Request
from starlette import status
from . import  models
from . import service
from fastapi.security import OAuth2PasswordRequestForm
from ..database.core import DBSession
from ..local_rate_limitter import limiter
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post("/login", response_model=models.Token)
@limiter.limit("10/minute")
async def login_for_access_token(request: Request,
                                   form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                   db: DBSession):
    return service.login_for_access_token(form_data, db)







