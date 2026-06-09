from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin, get_current_reviewer
from app.models import User
from app.schemas import (
    CandidateResponse, CandidateCreate, ScoreCreate, ScoreResponse,
    CandidateFilters
)
from app.services.candidate_service import CandidateService

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.get("", response_model=dict)
async def get_candidates(
    status: Optional[str] = Query(None, description="Filter by status (new/reviewed/hired/rejected)"),
    role_applied: Optional[str] = Query(None, description="Filter by role"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    keyword: Optional[str] = Query(None, description="Search in name, email, role"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Items per page (max 50)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List candidates with filters and pagination.
    """
    candidates, total_count = await CandidateService.get_candidates(
        db=db,
        status=status,
        role_applied=role_applied,
        skill=skill,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    
    # Convert to response schemas
    candidate_responses = []
    for candidate in candidates:
        # Only show internal_notes if user is admin
        if current_user.role != "admin":
            candidate.internal_notes = None
        
        candidate_responses.append(CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            role_applied=candidate.role_applied,
            status=candidate.status,
            skills=candidate.skills,
            internal_notes=candidate.internal_notes,
            created_at=candidate.created_at
        ))
    
    return {
        "items": candidate_responses,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size
    }

@router.get("/{candidate_id}", response_model=dict)
async def get_candidate_detail(
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get candidate details with scores.
    Reviewers see only their own scores, admins see all scores.
    """
    candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Get scores based on user role
    reviewer_id = None if current_user.role == "admin" else current_user.id
    scores = await CandidateService.get_candidate_scores(db, candidate_id, reviewer_id)
    
    # Get reviewer names for scores (admin view)
    score_responses = []
    for score in scores:
        # Get reviewer name
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == score.reviewer_id))
        reviewer = result.scalar_one_or_none()
        
        score_responses.append(ScoreResponse(
            id=score.id,
            candidate_id=score.candidate_id,
            category=score.category,
            score=score.score,
            reviewer_id=score.reviewer_id,
            reviewer_name=reviewer.full_name if reviewer else "Unknown",
            note=score.note,
            created_at=score.created_at
        ))
    
    # Prepare response (hide internal_notes from reviewers)
    return {
        "candidate": CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            role_applied=candidate.role_applied,
            status=candidate.status,
            skills=candidate.skills,
            internal_notes=candidate.internal_notes if current_user.role == "admin" else None,
            created_at=candidate.created_at
        ),
        "scores": score_responses,
        "user_role": current_user.role
    }

@router.post("/{candidate_id}/scores", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def submit_score(
    candidate_id: str,
    score_data: ScoreCreate,
    current_user: User = Depends(get_current_reviewer),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a score for a candidate.
    Accessible by reviewers and admins.
    """
    # Verify candidate exists
    candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Create score
    score = await CandidateService.create_score(
        db=db,
        candidate_id=candidate_id,
        reviewer_id=current_user.id,
        score_data=score_data
    )
    
    return ScoreResponse(
        id=score.id,
        candidate_id=score.candidate_id,
        category=score.category,
        score=score.score,
        reviewer_id=score.reviewer_id,
        reviewer_name=current_user.full_name,
        note=score.note,
        created_at=score.created_at
    )

@router.put("/{candidate_id}/notes")
async def update_internal_notes(
    candidate_id: str,
    notes: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update internal notes (Admin only).
    """
    candidate = await CandidateService.update_candidate_notes(db, candidate_id, notes)
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return {
        "message": "Internal notes updated successfully",
        "candidate_id": candidate_id,
        "notes": candidate.internal_notes
    }

@router.delete("/{candidate_id}")
async def soft_delete_candidate(
    candidate_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a candidate (Admin only).
    Sets deleted_at timestamp and status to 'archived'.
    """
    success = await CandidateService.soft_delete_candidate(db, candidate_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return {
        "message": "Candidate archived successfully",
        "candidate_id": candidate_id
    }