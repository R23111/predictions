from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from backend.database import SessionLocal
from starlette import status

from backend.services.authentication import (
    encrypt_password,
    decode_token,
)
from backend.core.config import settings
from backend.core.logger import logger
from backend.database import engine
from backend.models import user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/create_user", status_code=status.HTTP_201_CREATED, response_model=user.UserView)
async def create_as_super_user(
    user_create: user.UserCreate, access_token: Annotated[str, Depends(oauth2_bearer)]
) -> user.UserView:
    try:
        with SessionLocal() as db:
            existing_user = db.query(user.User).filter(user.User.username == (user_create.username)).first()
            if not existing_user:
                creator_role = decode_token(access_token).get("role")
                if creator_role != "admin":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Forbidden",
                    )
                user_create.password = encrypt_password(user_create.password)
                db_user = user.User.model_validate(user_create)
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                return user.UserView(success=True, is_admin=False, username=db_user.username)
    except HTTPException as e:
        raise e
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
