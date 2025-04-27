from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from FastAPI.app.database import Base


class HabitOrm(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    date_start: Mapped[str]
    status: Mapped[str]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))