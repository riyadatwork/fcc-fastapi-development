from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint


class UserCreate(BaseModel):
    email: EmailStr
    password: str


# Validation for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    

# Validate payload for Post
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True          # Include default value


# Good practice to control payload validation for different APIs
class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True     # Enable Pydantic to parse the ORM response


# Validate API response
# - only the defined fields below will be returned
class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut          # Include owner info in response

    class Config:
        orm_mode = True     # Enable Pydantic to parse the ORM response


# Validate the API response - include the number of votes/likes
class PostOut(BaseModel):
    Post: PostResponse      # Expects the PostResponse
    votes: int 

    class Config:
        orm_mode = True     # Enable Pydantic to parse the ORM response


# Validation of generated token
class Token(BaseModel):
    access_token: str
    token_type: str      


# Validation of the user_id embedded in the token
class TokenData(BaseModel):
    id: Optional[str] = None


# Post is either liked (1) or to-be-deleted (0)
class VoteInput(BaseModel):
    post_id: int
    dir: conint(le=1)   # conint: constrained integer     