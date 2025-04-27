from fastapi import FastAPI

from FastAPI.app.database import create_tables
from FastAPI.app.users.routers import user_router
from FastAPI.app.habits.routers import habit_router


async def lifespan(app):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(habit_router)


