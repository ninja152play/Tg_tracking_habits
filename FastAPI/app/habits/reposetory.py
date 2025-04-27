from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from FastAPI.app.habits.models import HabitOrm
from FastAPI.app.users.reposetory import get_user_by_tg_id


async def get_all_habits(user_id: int ,session: AsyncSession):
    stmt = select(HabitOrm).where(HabitOrm.user_id == user_id)
    result = await session.execute(stmt)
    return [habit for habit in result.scalars().all()]


async def create_habit(user_id: int, data: dict, session: AsyncSession):
    new_habit = HabitOrm(
        name=data['name'],
        date_start=datetime.now().strftime('%d-%m-%Y'),
        status='In progress',
        user_id=user_id
    )
    session.add(new_habit)
    await session.commit()
    await session.refresh(new_habit)
    return new_habit

async def edit_habit_name(user_id: int, data: dict, session: AsyncSession):
    stmt = select(HabitOrm).where(HabitOrm.user_id == user_id).where(HabitOrm.name == data['old_title'])
    result = await session.execute(stmt)
    habit = result.scalar_one_or_none()
    habit.name = data['new_title']
    await session.commit()
    await session.refresh(habit)
    return habit

async def edit_habit_status(user_id: int, data: dict, session: AsyncSession):
    stmt = select(HabitOrm).where(HabitOrm.user_id == user_id).where(HabitOrm.name == data['title'])
    result = await session.execute(stmt)
    habit = result.scalar_one_or_none()
    habit.status = 'Completed'
    await session.commit()
    await session.refresh(habit)
    return habit

async def delete_habit_by_name(user_id: int, data: dict, session: AsyncSession):
    stmt = select(HabitOrm).where(HabitOrm.user_id == user_id).where(HabitOrm.name == data['title'])
    result = await session.execute(stmt)
    habit = result.scalar_one_or_none()
    await session.delete(habit)
    await session.commit()
    return habit

async def get_all_progress_habits(tg_id: int, session: AsyncSession):
    user = await get_user_by_tg_id(tg_id, session)
    stmt = select(HabitOrm).where(HabitOrm.user_id == user.id).where(HabitOrm.status == 'In progress')
    result = await session.execute(stmt)
    return [habit.name for habit in result.scalars().all()]