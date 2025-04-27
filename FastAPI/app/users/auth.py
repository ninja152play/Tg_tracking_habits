from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .reposetory import get_user
from .dao import verify_password


async def authenticate_user(username: str, password: str, session: AsyncSession):
    user = await get_user(username, session)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    return user