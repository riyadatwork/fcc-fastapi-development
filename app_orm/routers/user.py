from ..models import User
from ..database import get_db
from ..schemas import UserCreate, UserOut
from ..utils import hash_this
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(user_payload: UserCreate, db: Session = Depends(get_db)):
    user_payload.password = hash_this(user_payload.password)

    user_query = db.query(User).filter(User.email == user_payload.email).first()
    if user_query:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'User {user_payload.email} already exist')

    new_user = User(**user_payload.dict())
    db.add(new_user)
    db.commit() 
    db.refresh(new_user)
    return new_user


@router.get('/{id}', response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id {id} not found')
    return user