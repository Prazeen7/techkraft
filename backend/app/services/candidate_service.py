from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.sql import func
from app.models import Candidate, Score, User
from app.schemas import CandidateCreate, ScoreCreate
from typing import Optional, List, Tuple
import uuid

class CandidateService:
    
    @staticmethod
    async def get_candidates(
        db: AsyncSession,
        status: Optional[str] = None,
        role_applied: Optional[str] = None,
        skill: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Candidate], int]:
        """
        Get candidates with filters and pagination.
        """
        # Build query
        query = select(Candidate).where(Candidate.deleted_at.is_(None))  # Soft delete filter
        
        # Apply filters at database level
        if status:
            query = query.where(Candidate.status == status)
        
        if role_applied:
            query = query.where(Candidate.role_applied == role_applied)
        
        if skill:
            # JSON array search in SQLite
            query = query.where(Candidate.skills.contains([skill]))
        
        if keyword:
            # Search in name, email, and role_applied
            keyword_filter = or_(
                Candidate.name.ilike(f"%{keyword}%"),
                Candidate.email.ilike(f"%{keyword}%"),
                Candidate.role_applied.ilike(f"%{keyword}%")
            )
            query = query.where(keyword_filter)
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Candidate.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        return candidates, total_count
    
    @staticmethod
    async def get_candidate_by_id(
        db: AsyncSession,
        candidate_id: str,
        include_deleted: bool = False
    ) -> Optional[Candidate]:
        """Get a single candidate by ID"""
        query = select(Candidate).where(Candidate.id == candidate_id)
        
        if not include_deleted:
            query = query.where(Candidate.deleted_at.is_(None))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_candidate_scores(
        db: AsyncSession,
        candidate_id: str,
        reviewer_id: Optional[str] = None
    ) -> List[Score]:
        """
        Get scores for a candidate.
        If reviewer_id is provided, only return that reviewer's scores.
        If None, return all scores (admin view).
        """
        query = select(Score).where(Score.candidate_id == candidate_id)
        
        if reviewer_id:
            query = query.where(Score.reviewer_id == reviewer_id)
        
        query = query.order_by(Score.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_score(
        db: AsyncSession,
        candidate_id: str,
        reviewer_id: str,
        score_data: ScoreCreate
    ) -> Score:
        """Create a new score for a candidate"""
        new_score = Score(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            reviewer_id=reviewer_id,
            category=score_data.category,
            score=score_data.score,
            note=score_data.note
        )
        
        db.add(new_score)
        await db.commit()
        await db.refresh(new_score)
        
        # Update candidate status to "reviewed" if it was "new"
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()
        
        if candidate and candidate.status == "new":
            candidate.status = "reviewed"
            await db.commit()
        
        return new_score
    
    @staticmethod
    async def create_candidate(
        db: AsyncSession,
        candidate_data: CandidateCreate
    ) -> Candidate:
        """Create a new candidate (for testing/seed data)"""
        new_candidate = Candidate(
            id=str(uuid.uuid4()),
            name=candidate_data.name,
            email=candidate_data.email,
            role_applied=candidate_data.role_applied,
            skills=candidate_data.skills,
            internal_notes=candidate_data.internal_notes or "",
            status="new"
        )
        
        db.add(new_candidate)
        await db.commit()
        await db.refresh(new_candidate)
        
        return new_candidate
    
    @staticmethod
    async def update_candidate_notes(
        db: AsyncSession,
        candidate_id: str,
        notes: str
    ) -> Optional[Candidate]:
        """Update internal notes (admin only)"""
        candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
        
        if not candidate:
            return None
        
        candidate.internal_notes = notes
        await db.commit()
        await db.refresh(candidate)
        
        return candidate
    
    @staticmethod
    async def get_candidate_by_email(db: AsyncSession, email: str) -> Optional[Candidate]:
        """Get a candidate by email"""
        result = await db.execute(select(Candidate).where(Candidate.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def soft_delete_candidate(
        db: AsyncSession,
        candidate_id: str
    ) -> bool:
        """Soft delete a candidate (set deleted_at timestamp)"""
        candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
        
        if not candidate:
            return False
        
        from datetime import datetime
        candidate.deleted_at = datetime.utcnow()
        candidate.status = "archived"
        await db.commit()
        
        return True