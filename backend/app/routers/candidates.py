from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin, get_current_reviewer
from app.models import User
from app.schemas import (
    CandidateResponse, CandidateCreate, ScoreCreate, ScoreResponse,
    CandidateFilters
)
from app.services.candidate_service import CandidateService

from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

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
    """
    # Verify candidate exists
    candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Handle system operations (admin only)
    if score_data.category.startswith("__"):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required for system operations"
            )
        
        # Update internal notes
        if score_data.category == "__internal_notes__":
            candidate.internal_notes = score_data.note
            await db.commit()
            return ScoreResponse(
                id="system",
                candidate_id=candidate_id,
                category="internal_notes",
                score=0,
                reviewer_id=current_user.id,
                reviewer_name=current_user.full_name,
                note=f"Internal notes updated",
                created_at=datetime.utcnow()
            )
        
        # Update status
        elif score_data.category == "__status__":
            valid_statuses = ["new", "reviewed", "hired", "rejected"]
            if score_data.note not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            candidate.status = score_data.note
            await db.commit()
            return ScoreResponse(
                id="system",
                candidate_id=candidate_id,
                category="status_update",
                score=0,
                reviewer_id=current_user.id,
                reviewer_name=current_user.full_name,
                note=f"Status changed to {score_data.note}",
                created_at=datetime.utcnow()
            )
        
        # Soft delete (archive)
        elif score_data.category == "__archive__":
            candidate.status = "archived"
            candidate.deleted_at = datetime.utcnow()
            await db.commit()
            return ScoreResponse(
                id="system",
                candidate_id=candidate_id,
                category="archive",
                score=0,
                reviewer_id=current_user.id,
                reviewer_name=current_user.full_name,
                note="Candidate archived",
                created_at=datetime.utcnow()
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown system operation"
        )
    
    # Regular score submission
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


@router.post("/{candidate_id}/summary")
async def generate_ai_summary(
    candidate_id: str,
    current_user: User = Depends(get_current_reviewer),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger mock AI summary generation.
    Simulates an async LLM call with 2s delay.
    """
    # Verify candidate exists
    candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    try:
        # Generate summary (includes 2 second delay)
        summary = await CandidateService.generate_ai_summary(db, candidate_id)
        
        return {
            "success": True,
            "summary": summary,
            "message": "AI summary generated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )

@router.get("/{candidate_id}/stream")
async def stream_score_updates(
    candidate_id: str,
    current_user: User = Depends(get_current_reviewer),
    db: AsyncSession = Depends(get_db)
):
    """
    SSE endpoint that streams score updates in real-time.
    Stretch goal: Shows real-time score updates as they happen.
    """
    # Verify candidate exists
    candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # For reviewers, only stream their own scores
    # For admins, stream all scores
    reviewer_id = None if current_user.role == "admin" else current_user.id
    
    # Create streaming response
    async def event_generator():
        async for event in CandidateService.stream_score_updates(db, candidate_id, reviewer_id):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )