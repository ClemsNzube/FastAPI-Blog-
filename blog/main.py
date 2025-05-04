from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from .schemas import Blog, ShowBlog, ListBlog
from .database import engine, SessionLocal
from fastapi.openapi.models import SecuritySchemeType
from fastapi.security import OAuth2PasswordBearer
from . import models
from .models import User
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from . import auth, schemas, utils
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter

models.Base.metadata.create_all(engine)

app = FastAPI(
    title="Blog API",
    description="API for managing blog posts",
    version="1.0.0",
    openapi_tags=[
        {"name": "blogs", "description": "Blog operations"},
        {"name": "users", "description": "User operations"},
    ],
    openapi_security=[{"Bearer": []}]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.openapi_security_schemes = {
    "Bearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}

blog_router = APIRouter(prefix="/blog", tags=["blogs"])
auth_router = APIRouter(tags=["authentication"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BlogViewSet:
    @staticmethod
    @blog_router.post("", status_code=status.HTTP_201_CREATED)
    def create(request: Blog, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
        new_blog = models.Blog(
            title=request.title,
            body=request.body,
            published=datetime.now(),
            is_published=True,
            user_id=current_user.id
        )
        db.add(new_blog)
        db.commit() 
        db.refresh(new_blog)
        return new_blog

    @staticmethod
    @blog_router.get("", response_model=ListBlog)
    def index(db: Session = Depends(get_db), limit: Optional[int] = 10, sort: Optional[str] = "asc"):
        blogs = db.query(models.Blog).filter(models.Blog.is_published == True).limit(limit).all()
        return {"data": blogs, "sort": sort}
    
    @staticmethod
    @blog_router.get("/{id}", response_model=ShowBlog)
    def show(id: int, db: Session = Depends(get_db)):
        blog = db.query(models.Blog).filter(models.Blog.id == id).first()
        if not blog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
        return blog

    @staticmethod
    @blog_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    def destroy(id: int, db: Session = Depends(get_db)):
        blog = db.query(models.Blog).filter(models.Blog.id == id)
        if not blog.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
        blog.delete(synchronize_session=False)
        db.commit()
        return {"message": "Blog deleted successfully"}

    @staticmethod
    @blog_router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
    def update(id: int, request: Blog, db: Session = Depends(get_db)):
        blog = db.query(models.Blog).filter(models.Blog.id == id)
        if not blog.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
        blog.update(request.model_dump())
        db.commit()
        return {"message": "Blog updated successfully", "data": blog.first()}
    

class UserViewSet:
    @staticmethod
    @auth_router.post("/users", response_model=schemas.User)
    def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
            
        hashed_password = utils.get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            name=user.name,
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    @auth_router.post("/login")
    def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        if not user or not utils.verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = auth.create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

app.include_router(blog_router)
app.include_router(auth_router)
