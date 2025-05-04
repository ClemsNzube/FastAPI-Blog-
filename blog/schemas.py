from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Blog(BaseModel):
    title: str
    body: str
    published: Optional[datetime] = None

class ShowBlog(Blog):
    class Config:
        from_attributes = True

class ListBlog(BaseModel):
    data: List[ShowBlog]
    sort: Optional[str] = None

    class Config:
        from_attributes = True