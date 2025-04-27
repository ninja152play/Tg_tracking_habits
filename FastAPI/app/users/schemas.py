from pydantic import BaseModel


class SUserCreate(BaseModel):
    tg_id: int
    name: str
    username: str
    password: str


class SToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str