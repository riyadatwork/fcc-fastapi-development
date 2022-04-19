from ..models import Post, User, Vote
from ..database import get_db
from ..schemas import PostCreate, PostResponse, PostOut
from ..oauth2 import get_current_user
from typing import List, Optional
from fastapi import Depends, status, HTTPException, Response, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.get('/', response_model=List[PostOut])
# @router.get('/')
# @router.get('/', response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    limit: int = 10,    # Query parameter to limit post to display
                    skip: int = 0,      # Query parameter on how many post to skip
                    search: Optional[str] = ""):  # Optional query parameter

    # Use SQLAlchemy limit, offset, contains methods
    # posts = db.query(Post).filter(Post.title.contains(
    #     search)).limit(limit).offset(skip).all()

    # Validate the response - which include the vote count &
    # enable query parameters limit, offset, search
    posts = db.query(Post, func.count(Vote.user_id).label('votes')).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id).filter(
            Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_posts(post_payload: PostCreate,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):   # Verified user
    # print(current_user.id, current_user.email)
    new_post = Post(owner_id=current_user.id,
                    **post_payload.dict())  # Include owner_id
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get('/{id}', response_model=PostOut)
# @router.get('/{id}', response_model=PostResponse)
async def get_post(id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    # post = db.query(Post).filter(Post.id == id).first()

    post = db.query(Post, func.count(Vote.user_id).label('votes')).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id).having(
        Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found')
    return post


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    post_object = db.query(Post).filter(Post.id == id)
    post = post_object.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found')
    # Only the post owner can delete the post
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'not authorized to perform this action')

    post_object.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{id}', response_model=PostResponse)
async def update_post(id: int, post_payload: PostCreate,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    post_object = db.query(Post).filter(Post.id == id)
    post_to_update = post_object.first()

    if post_to_update == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found')
    # Only post owner can update the post
    if post_to_update.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'not authorized to perform this action')

    post_object.update(post_payload.dict(), synchronize_session=False)
    db.commit()
    return post_object.first()
