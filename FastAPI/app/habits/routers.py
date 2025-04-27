from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends, status, Request, HTTPException

from .reposetory import get_all_habits, create_habit, edit_habit_name, edit_habit_status, delete_habit_by_name, \
    get_all_progress_habits

from FastAPI.app.users.models import UserOrm
from FastAPI.app.users.dao import get_current_user
from FastAPI.app.database import get_db


habit_router = APIRouter(
    prefix="/api",
    tags=["Habits"],
)


@habit_router.get("/habits")
async def get_habit(
        current_user: Annotated[UserOrm, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db)]
):
    habits = await get_all_habits(current_user.id, session)
    response = [{'name': habit.name, 'id': habit.id, 'date': habit.date_start, 'status': habit.status} for habit in habits]
    return response

@habit_router.post("/habits")
async def add_habit(
        data: Request,
        current_user: Annotated[UserOrm, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db)]
):
    data = await data.json()
    habit = await create_habit(current_user.id, data, session)
    if habit:
        return
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

@habit_router.patch("/habits")
async def change_habit(
        data: Request,
        current_user: Annotated[UserOrm, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db)]
):
    data = await data.json()
    habit = await edit_habit_name(current_user.id, data, session)
    if habit:
        return
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

@habit_router.put("/habits")
async def change_habit_status(
        data: Request,
        current_user: Annotated[UserOrm, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db)]
):
    data = await data.json()
    habit = await edit_habit_status(current_user.id, data, session)
    if habit:
        return
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

@habit_router.delete("/habits")
async def delete_habit(
        data: Request,
        current_user: Annotated[UserOrm, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db)]
):
    data = await data.json()
    habit = await delete_habit_by_name(current_user.id, data, session)
    if habit:
        return
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

@habit_router.get('/notification/{tg_id}')
async def send_notification(
        tg_id: int,
        session: Annotated[AsyncSession, Depends(get_db)]
):
    response = await get_all_progress_habits(tg_id, session)
    return response
