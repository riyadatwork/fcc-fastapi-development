from .schemas import TokenData
from .database import get_db
from .models import User
from .config import settings
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Generated via: 'openssl rand -hex 32'
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Extract the user_id from the token
def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('user_id')
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception
    
    return token_data


# Calls verify_access_token to get the user_id - based on the given token
def get_current_user(token: str = Depends(oauth2_scheme), 
                     db: Session = Depends(get_db)):
    # Pass this exception to verify_access_token and throw this if any exception encountered
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail='Could not validate credentials', 
        headers={'WWW-Authenticate': 'Bearer'}
    )

    # Validate that the id from the token exist and return the user instance
    token = verify_access_token(token, credentials_exception)
    user = db.query(User).filter(User.id == token.id).first()

    return user