from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi.exceptions import HTTPException
from fastapi import status, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from FastAPI.app.config import BASE_DIR, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM
from FastAPI.app.database import get_db
from .reposetory import get_user



with open("".join(str(BASE_DIR) + "/RSA/private.pem"), "rb") as f:
    PRIVATE_KEY = f.read()

with open("".join(str(BASE_DIR) + "/RSA/public.pem"), "rb") as f:
    PUBLIC_KEY = f.read()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

async def create_token(username: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + access_token_expires,
        "type": "access"
    }
    access_token = jwt.encode(access_payload, PRIVATE_KEY, algorithm=ALGORITHM)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + refresh_token_expires,
        "type": "refresh"
    }
    refresh_token = jwt.encode(refresh_payload, PRIVATE_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is invalid")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[AsyncSession, Depends(get_db)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = await verify_token(token)
    if not payload:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = await get_user(username=username, session=session)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user