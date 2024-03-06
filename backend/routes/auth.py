from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from passlib.context import CryptContext
from backend.database import SessionLocal
from starlette import status

from backend.services.authentication import (
    check_password,
    encrypt_password,
    generate_token,
    decode_token,
)
from backend.core.config import settings
from backend.core.logger import logger
from backend.database import SessionLocal, engine
from backend.models import token
from backend.models import user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=user.UserView)
async def create_user(
    user_create: user.UserCreate,
) -> user.UserView:
    try:
        with SessionLocal() as db:
            existing_user = db.query(user.User).filter(user.User.username == (user_create.username)).first()
            if not existing_user:
                if user_create.is_admin:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid role",
                    )
                user_create.password = encrypt_password(user_create.password)
                db_user = user.User.model_validate(user_create)
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                return user.UserView(success=True, is_admin=False, username=db_user.username)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from e
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already exists",
    )


@router.post("/token", response_model=token.Token)
async def login_for_access_token(
    access_token: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> token.Token:
    with SessionLocal() as db:
        db_user = db.query(user.User).where(user.User.username == access_token.username).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_NOT_FOUND,
                detail="Incorrect username",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not check_password(access_token.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_token = generate_token(username=access_token.username, is_admin=db_user.is_admin)
        return token.Token(access_token=user_token, token_type="bearer")


@router.get("/me")
async def read_users_me(
    access_token: Annotated[str, Depends(oauth2_bearer)],
) -> user.UserRead:
    try:
        payload = decode_token(access_token)
        username: str | None = payload.get("user")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = token.TokenData(username=username, role=payload.get("role"))
    except JWTError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    with SessionLocal() as db:
        db_user = db.query(user.User).filter(user.User.username == token_data.username).first()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user.UserRead(
            id=db_user.id,
            username=db_user.username,
            is_admin=db_user.is_admin,
        )
