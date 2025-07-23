from typing import Annotated
from fastapi import APIRouter, Depends, Request
from . import  model
from . import service
from fastapi.security import OAuth2PasswordRequestForm
from ..database.core import DBSession
from ..local_rate_limitter import limiter
router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

@router.post("/login", response_model=model.Token)
@limiter.limit("100/minute")
async def login_for_access_token(request: Request,
                                   form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                   db: DBSession):
    return await service.login_for_access_token(form_data, db)







