from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="user")  # admin, user
    api_key = Column(String(255), unique=True, index=True)
    check_limit = Column(Integer, default=1000)
    checks_used = Column(Integer, default=0)
    daily_checks = Column(Integer, default=0)
    last_check_reset = Column(DateTime, default=func.now())
    status = Column(String(20), default="active")  # active, suspended
    created_at = Column(DateTime, default=func.now())

    logs = relationship("CheckLog", back_populates="user")
    api_logs = relationship("APILog", back_populates="user")

class CheckLog(Base):
    __tablename__ = "check_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    combo = Column(String(255))
    result = Column(String(20))  # working, invalid, banned, error
    detail = Column(Text)
    proxy_used = Column(String(100))
    timestamp = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="logs")

class APILog(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String(100))
    method = Column(String(10))
    status_code = Column(Integer)
    timestamp = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="api_logs")