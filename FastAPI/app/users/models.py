from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text, BigInteger

from FastAPI.app.database import Base


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str]

    is_active: Mapped[bool] = mapped_column(default=True, server_default=text('true'))