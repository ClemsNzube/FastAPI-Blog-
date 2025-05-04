from .database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    blogs = relationship("Blog", back_populates="creator")


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    body = Column(Text)
    published = Column(DateTime, default=datetime.now, nullable=True)
    is_published = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    creator = relationship("User", back_populates="blogs")