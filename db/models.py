from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, autoincrement=True, primary_key=True)
    tg_id = Column(Integer, unique=True)


class Statistics(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    url = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean)
