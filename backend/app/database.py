from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv
from sqlalchemy import select 

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine for SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create default admin user
    await create_default_admin()
    

async def create_default_admin():
    """Create default admin user if not exists"""
    from app.models import User
    from app.auth import get_password_hash
    
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv( "ADMIN_PASSWORD")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == admin_email))
        existing_admin = result.scalar_one_or_none()
        
        if not existing_admin:
            import uuid
            admin_user = User(
                id=str(uuid.uuid4()),
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                full_name="System Administrator",
                role="admin"
            )
            session.add(admin_user)
            await session.commit()
            print(f"Default admin created: {admin_email}")
        else:
            print(f"Admin already exists: {admin_email}")