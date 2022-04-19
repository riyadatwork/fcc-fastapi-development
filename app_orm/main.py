from .models import Base
from .database import engine
from .routers import post, user, auth, vote
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


#-- Comment the following code to prevent SQLAlchemy from creating the tables
#-- as we want Alembic to handle any DB migrations
# Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'])

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get('/')
def root():
    return {"message": "Welcome to my FastAPI Home"}