from typing import Annotated
from fastapi.routing import APIRouter
from fastapi import Depends, status, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException

from .auth import authenticate_user
from .dao import get_password_hash, create_token, verify_token
from .models import UserOrm
from .reposetory import get_user, delete_user_by_id, get_user_by_tg_id
from .schemas import SUserCreate, SToken
from FastAPI.app.database import get_db


user_router = APIRouter(
    prefix="/api",
    tags=["Users"],
)


@user_router.post("/register")
async def register(
        user: Request,
        session: Annotated[AsyncSession, Depends(get_db)],
):
    user = await user.json()
    exists_user = await get_user(user.get('username'), session)
    if exists_user:
        print(exists_user)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    exists_user = await get_user_by_tg_id(user.get('tg_id'), session)
    if exists_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    hashed_password = get_password_hash(user.get('password'))
    print(user['tg_id'])
    user = UserOrm(
        name=user.get('name'),
        username=user.get('username'),
        hashed_password=hashed_password,
        tg_id=user.get('tg_id'),
        is_active=True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return await create_token(user.username)

@user_router.post("/login")
async def login(
        form_data: Request,
        session: Annotated[AsyncSession, Depends(get_db)],
):
    form_data = await form_data.json()
    user = await authenticate_user(form_data["username"], form_data["password"], session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return await create_token(user.username)

@user_router.post("/refresh-token", response_model=SToken)
async def refresh_token(
        session: Annotated[AsyncSession, Depends(get_db)],
        refresh_token: str = Body(..., embed=True),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

    payload = await verify_token(refresh_token)
    if not payload or payload.get('type') != 'refresh':
        raise credentials_exception

    username = payload.get('sub')
    if username is None:
        raise credentials_exception

    user = await get_user(username, session)
    if not user or not user.is_active:
        raise credentials_exception

    return await create_token(username)




