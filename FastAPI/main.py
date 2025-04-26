from fastapi import FastAPI

from app.database import create_tables


async def lifespan(app):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

