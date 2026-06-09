from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth import authenticate_user, create_access_token, get_password_hash, get_user_by_email
from typing import List
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    IMPORTANT: Role is ALWAYS set to "reviewer" - never accepted from client.
    """
    # Log the received data
    logger.info(f"Received registration request")
    logger.info(f"Email: {user_data.email}")
    logger.info(f"Full name: {user_data.full_name}")
    logger.info(f"Password length: {len(user_data.password)}")
    
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        logger.warning(f"User already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user - role is HARDCODED to "reviewer"
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role="reviewer"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"User created successfully: {new_user.id}")
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            created_at=new_user.created_at
        )
    )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password"""
    user = await authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at
        )
    )

@router.post("/create-admin", status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Create an admin user (should be protected or only used during initial setup).
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, admin_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    import uuid
    new_admin = User(
        id=str(uuid.uuid4()),
        email=admin_data.email,
        password_hash=get_password_hash(admin_data.password),
        full_name=admin_data.full_name,
        role="admin"
    )
    
    db.add(new_admin)
    await db.commit()
    
    return {"message": "Admin user created successfully", "email": admin_data.email}