from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

@app.get("/blog")
def index(limit: Optional[int] = 10, published: Optional[bool] = True, sort: Optional[str] = "asc"):
    if published:
        
        return {"data": f"{limit} blog posts from the db", "published": published, "sort": sort}
    else:
        return {"data": "No published blog posts", "published": published, "sort": sort}




@app.get("/blog/{id}")
def show(id: int):
    return {"data": id}

@app.get("/blog/{id}/comments")
def comments(id: int, limit: int = 10):
    if id == 1:
        return {"comments": ['1', '2', '3', '4']}
    else:
        return {"comments": {'1', '2'}}
    

class Blog(BaseModel):
    title: str
    body: str
    published: Optional[bool] = True


@app.post("/blog")
def create(request: Blog):
    return {request.title, request.body, request.published} 