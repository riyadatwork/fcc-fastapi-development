from ..database import get_db
from ..schemas import UserLogin, Token
from ..models import User
from ..utils import verify
from ..oauth2 import create_access_token
from fastapi import Depends, status, HTTPException, Response, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm returns attributes 'username' & 'password'
    user = db.query(User).filter(User.email == user_credentials.username).first()

    # Check if user exist or password is correct
    if not user or not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Invalid credentials')

    # Create and return a token. Also add user_id as part of the token data
    access_token = create_access_token(data={'user_id': user.id})
    return {'access_token': access_token,
            'token_type': 'bearer'}
