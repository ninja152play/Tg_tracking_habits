from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from FastAPI.app.users.models import UserOrm


async def get_user(username: str, session: AsyncSession):
    stmt = select(UserOrm).where(UserOrm.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_tg_id(tg_id: int, session: AsyncSession):
    stmt = select(UserOrm).where(UserOrm.tg_id == tg_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def delete_user_by_id(user_id: int, session: AsyncSession):
    stmt = select(UserOrm).where(UserOrm.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    await session.delete(user)
    await session.commit()