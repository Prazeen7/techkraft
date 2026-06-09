from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.sql import func
from app.models import Candidate, Score, User
from app.schemas import CandidateCreate, ScoreCreate
from typing import Optional, List, Tuple
import uuid
import asyncio
import random
from datetime import datetime
from typing import Dict, Any

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
    
    @staticmethod
    async def generate_ai_summary(
        db: AsyncSession,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Mock AI summary generation with 2 second delay.
        Simulates calling an external LLM API.
        """
        # Simulate 2 second delay (as required by requirements)
        await asyncio.sleep(2)
        
        # Fetch candidate data
        candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
        
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Fetch scores for this candidate
        scores = await CandidateService.get_candidate_scores(db, candidate_id, reviewer_id=None)
        
        # Calculate average score if any scores exist
        avg_score = None
        if scores:
            avg_score = sum(s.score for s in scores) / len(scores)
        
        # Generate mock AI summary based on candidate data
        summary_templates = [
            f"{candidate.name} demonstrates strong potential for the {candidate.role_applied} position. "
            f"Technical skills in {', '.join(candidate.skills[:3]) if candidate.skills else 'software development'} "
            f"{'and more' if len(candidate.skills) > 3 else ''} "
            f"align well with our requirements.",
            
            f"Based on the assessment, {candidate.name} shows {'excellent' if avg_score and avg_score > 4 else 'good' if avg_score and avg_score > 3 else 'adequate'} "
            f"performance across evaluated categories. "
            f"The candidate's background in {candidate.skills[0] if candidate.skills else 'technology'} "
            f"is particularly relevant for the {candidate.role_applied} role.",
            
            f"AI Analysis: {candidate.name} has {'strong' if len(candidate.skills) > 5 else 'solid'} technical foundations. "
            f"Recommended for {'next round' if avg_score and avg_score > 3.5 else 'technical screening'} based on current evaluation data.",
            
            f"Summary for {candidate.name}: {'Experienced' if len(candidate.skills) > 4 else 'Emerging'} professional "
            f"specializing in {candidate.skills[0] if candidate.skills else 'software development'}. "
            f"Applied for {candidate.role_applied} position with {len(scores)} score{'s' if len(scores) != 1 else ''} recorded."
        ]
        
        # Add score-based analysis if scores exist
        score_analysis = ""
        if scores and avg_score:
            categories = list(set(s.category for s in scores))
            if avg_score >= 4.5:
                score_analysis = f" Outstanding performance with average score {avg_score:.1f}/5. "
            elif avg_score >= 3.5:
                score_analysis = f" Good performance with average score {avg_score:.1f}/5. "
            elif avg_score >= 2.5:
                score_analysis = f" Satisfactory performance with average score {avg_score:.1f}/5. "
            else:
                score_analysis = f" Needs improvement with average score {avg_score:.1f}/5. "
            
            if categories:
                score_analysis += f" Evaluated in: {', '.join(categories)}."
        
        # Add skill recommendations
        skill_recommendations = ""
        if candidate.skills and len(candidate.skills) < 3:
            skill_recommendations = f" Consider upskilling in additional areas like cloud computing or system design."
        elif avg_score and avg_score < 3:
            skill_recommendations = f" Recommend additional training in {candidate.skills[0] if candidate.skills else 'core technologies'}."
        
        # Generate final summary
        base_summary = random.choice(summary_templates)
        if score_analysis:
            base_summary += score_analysis
        if skill_recommendations:
            base_summary += skill_recommendations
        
        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.name,
            "email": candidate.email,
            "role": candidate.role_applied,
            "status": candidate.status,
            "summary": base_summary,
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": {
                "total_scores": len(scores),
                "average_score": round(avg_score, 2) if avg_score else None,
                "categories_evaluated": list(set(s.category for s in scores)) if scores else [],
                "skills_assessed": candidate.skills[:3] if candidate.skills else []
            }
        }                       


    @staticmethod
    async def stream_score_updates(
        db: AsyncSession,
        candidate_id: str,
        reviewer_id: str = None
    ):
        """
        Generator for SSE streaming of score updates.
        This is a generator function for StreamingResponse.
        """
        import asyncio
        import json
        from sqlalchemy import select
        from app.models import Score, User
        
        # Initial connection message
        yield f"data: {json.dumps({'event': 'connected', 'data': f'Monitoring score updates for candidate {candidate_id}'})}\n\n"
        
        # Get initial scores
        query = select(Score).where(Score.candidate_id == candidate_id)
        if reviewer_id:
            query = query.where(Score.reviewer_id == reviewer_id)
        
        result = await db.execute(query)
        previous_scores = result.scalars().all()
        previous_score_ids = {s.id for s in previous_scores}
        
        # Stream for 30 seconds (10 iterations * 3 seconds)
        for i in range(10):
            await asyncio.sleep(3)
            await db.commit()
            
            # Check for new scores
            result = await db.execute(query)
            current_scores = result.scalars().all()
            current_score_ids = {s.id for s in current_scores}
            new_score_ids = current_score_ids - previous_score_ids
            
            if new_score_ids:
                new_scores = [s for s in current_scores if s.id in new_score_ids]
                for score in new_scores:
                    reviewer_result = await db.execute(
                        select(User).where(User.id == score.reviewer_id)
                    )
                    reviewer = reviewer_result.scalar_one_or_none()
                    
                    event_data = {
                        'event': 'new_score',
                        'data': {
                            'id': score.id,
                            'category': score.category,
                            'score': score.score,
                            'reviewer_id': score.reviewer_id,
                            'reviewer_name': reviewer.full_name if reviewer else 'Unknown',
                            'note': score.note,
                            'timestamp': score.created_at.isoformat()
                        }
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                
                previous_score_ids = current_score_ids
            else:
                yield f"data: {json.dumps({'event': 'heartbeat', 'data': 'No new score updates'})}\n\n"
        
        # End of stream
        yield f"data: {json.dumps({'event': 'end', 'data': 'Stream monitoring ended'})}\n\n"