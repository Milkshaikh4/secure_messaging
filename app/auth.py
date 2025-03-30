import os
import time
import jwt 
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "my_jwt_secret")
JWT_ALGORITHM = "HS256"

token_auth_scheme = HTTPBearer()

def create_jwt_token(user_id: str) -> str:
    """Generate a JWT for the given user_id."""
    payload = {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600  # 1 hour expiry
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt_token(token: str) -> dict:
    """Decode and return the payload of the given JWT."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> str:
    """
    Extract user_id (sub) from the JWT included in the Authorization header.
    """
    token = credentials.credentials
    payload = decode_jwt_token(token)
    user_id = payload["sub"]
    return user_id
