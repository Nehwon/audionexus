"""
Routes d'authentification pour l'API.
"""
from __future__ import annotations
from datetime import timedelta
from typing import Any, TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.config import settings

# Import différé pour éviter les imports circulaires
if TYPE_CHECKING:
    from app.db.models.base import User, UserCreate, UserInDB, Token
    from app import crud, models

router = APIRouter()

@router.post("/login/access-token", response_model="Token")
async def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud.crud_user.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/login/test-token", response_model='UserInDB')
async def test_token(current_user: 'models.User' = Depends(deps.get_current_user)) -> Any:
    """
    Test access token.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Test token endpoint called with user: {current_user.username}")
    return current_user

@router.post("/register", response_model='UserInDB')
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: 'UserCreate',
) -> Any:
    """
    Create new user.
    """
    user = crud.crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.crud_user.create_user(db=db, user=user_in)
    return user
