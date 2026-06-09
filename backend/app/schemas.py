from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Candidate schemas
class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    role_applied: str
    skills: List[str] = []
    internal_notes: Optional[str] = ""

class CandidateResponse(BaseModel):
    id: str
    name: str
    email: str
    role_applied: str
    status: str
    skills: List[str]
    internal_notes: Optional[str] = None  # Only visible to admin
    created_at: datetime

# Score schemas
class ScoreCreate(BaseModel):
    category: str
    score: int = Field(..., ge=1, le=5)
    note: Optional[str] = ""

class ScoreResponse(BaseModel):
    id: str
    candidate_id: str
    category: str
    score: int
    reviewer_id: str
    reviewer_name: Optional[str] = None
    note: str
    created_at: datetime

# Query params
class CandidateFilters(BaseModel):
    status: Optional[str] = None
    role_applied: Optional[str] = None
    skill: Optional[str] = None
    keyword: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=50)