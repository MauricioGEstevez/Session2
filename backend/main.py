from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 300  # 5 minutes

# Security warning for default SECRET_KEY
if SECRET_KEY == "your-secret-key-change-in-production":
    print("⚠️  WARNING: Using default SECRET_KEY. Change this in production by setting the SECRET_KEY environment variable.")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create FastAPI app
app = FastAPI(
    title="JWT Authentication API",
    description="FastAPI backend with JWT authentication",
    version="0.1.0"
)

# Pydantic models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    username: str
    password: str


class User(BaseModel):
    username: str
    disabled: Optional[bool] = None


# In-memory user database (for demo/development purposes only)
# ⚠️  SECURITY: In production, store user credentials in a secure database with proper hashing
# Default credentials: username=admin, ****** (for testing only)
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": "$2b$12$c3LUJan19LSLyR0GqfANOe2y5B0zW5RDXO4suTRuqBBX2WobpErly",  # admin123
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with 7 days expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Check token type if it's a refresh token
        if token_type == "refresh" and payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Endpoints
@app.post("/login", response_model=Token, tags=["Authentication"])
async def login(credentials: LoginRequest):
    """
    Login endpoint that accepts username and password.
    Returns JWT access token and refresh token with 300 seconds expiration.
    
    Default credentials:
    - username: admin
    - password: admin123
    """
    # Check if user exists
    user = USERS_DB.get(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is disabled
    if user.get("disabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": credentials.username},
        expires_delta=timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    refresh_token = create_refresh_token(data={"sub": credentials.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
    }


@app.post("/refresh", response_model=Token, tags=["Authentication"])
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh token endpoint that accepts a refresh token.
    Returns a new access token with 300 seconds expiration.
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    username = payload.get("sub")
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
    }


@app.get("/protected", tags=["Protected"])
async def protected_route(request: Request):
    """
    Protected route that requires a valid access token.
    To use this route, include the token in the Authorization header:
    Authorization: ******
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "******" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: ******",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    payload = verify_token(token)
    username = payload.get("sub")
    
    return {
        "message": "This is a protected route",
        "username": username
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "jwt-auth-backend"}


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "JWT Authentication Backend",
        "version": "0.1.0",
        "endpoints": {
            "login": "/login (POST)",
            "refresh": "/refresh (POST)",
            "health": "/health (GET)",
            "docs": "/docs (Swagger UI)",
            "redoc": "/redoc (ReDoc)",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
