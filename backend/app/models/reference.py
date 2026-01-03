from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    category: Mapped[str] = mapped_column(String(32), default="sport")
    is_user_defined: Mapped[bool] = mapped_column(Boolean, default=False)

    entities: Mapped[list["SportEntity"]] = relationship("SportEntity", back_populates="sport")


class SportEntity(Base):
    __tablename__ = "sport_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sport_id: Mapped[int] = mapped_column(Integer, ForeignKey("sports.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(256), unique=True)
    entity_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_user_defined: Mapped[bool] = mapped_column(Boolean, default=False)

    sport: Mapped[Sport] = relationship("Sport", back_populates="entities")
    aliases: Mapped[list["SportAlias"]] = relationship(
        "SportAlias", back_populates="entity", cascade="all, delete-orphan"
    )


class SportAlias(Base):
    __tablename__ = "sport_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("sport_entities.id", ondelete="CASCADE"), index=True)
    alias: Mapped[str] = mapped_column(String(256))
    normalized_alias: Mapped[str] = mapped_column(String(256), index=True)

    entity: Mapped[SportEntity] = relationship("SportEntity", back_populates="aliases")
