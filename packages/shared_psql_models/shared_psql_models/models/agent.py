from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shared_psql_models.base import Base, JSONBCompat


class Agent(Base):
    """Authoritative definition for agents stored in shared_psql."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[dict] = mapped_column(JSONBCompat, nullable=False, default=dict)
    activation_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    rate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


__all__ = ["Agent"]


