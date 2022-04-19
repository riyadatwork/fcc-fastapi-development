from requests import Response
from ..models import User, Post, Vote
from ..database import get_db
from ..schemas import VoteInput
from ..oauth2 import get_current_user
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/vote',
    tags=['Vote']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def vote(vote_payload: VoteInput,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    # Check if post exist
    post_query = db.query(Post).filter(Post.id == vote_payload.post_id).first()
    if not post_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post {vote_payload.post_id} does not exit')

    # Check if entry in table votes exist for the current user     
    vote_query = db.query(Vote).filter(Vote.post_id == vote_payload.post_id, \
                                       Vote.user_id == current_user.id)
    vote_found = vote_query.first()

    # If post is liked    
    if vote_payload.dir == 1:
        # If entry already exist in table votes, raise exception
        if vote_found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f'user {current_user.id} has already voted on post {vote_payload.post_id}')
        # Create new entry in table votes
        new_vote = Vote(user_id=current_user.id, post_id=vote_payload.post_id)
        db.add(new_vote)
        db.commit()
        return {'message': 'vote successfully added'}
    # If post is to-be-deleted   
    else:
        if not vote_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='vote does not exist')
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {'message': 'vote successfully deleted'}