"""
Seed script to populate the database with sample candidates
Run this script to add test data to your database
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models import Candidate, User, Score
from app.auth import get_password_hash
import uuid
from datetime import datetime, timedelta
import random

# Configuration
NUM_CANDIDATES = 50

# Sample data for random generation
FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry",
    "Iris", "Jack", "Karen", "Leo", "Maria", "Nathan", "Olivia", "Peter",
    "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xavier",
    "Yara", "Zack", "Ava", "Ben", "Chloe", "Daniel", "Eva", "Felix",
    "Gina", "Hugo", "Ivy", "James", "Kate", "Liam", "Mia", "Noah",
    "Oscar", "Penny", "Quincy", "Ruby", "Steve", "Taylor", "Uma", "Vera",
    "Will", "Xena", "Yasmin", "Zoe"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Walker", "Hall", "Allen", "Young", "King", "Wright", "Scott",
    "Green", "Baker", "Adams", "Nelson", "Carter", "Mitchell", "Roberts",
    "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
    "Stewart", "Morris", "Rogers", "Reed", "Cook", "Bell", "Cooper"
]

ROLES = [
    "Full Stack Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "DevOps Engineer",
    "Data Engineer",
    "Mobile Developer",
    "QA Engineer",
    "Security Engineer"
]

SKILL_SETS = {
    "Full Stack Engineer": [
        ["Python", "React", "FastAPI", "PostgreSQL", "Docker"],
        ["JavaScript", "Node.js", "React", "MongoDB", "AWS"],
        ["Python", "Django", "Vue.js", "PostgreSQL", "Redis"],
        ["TypeScript", "Next.js", "NestJS", "PostgreSQL", "Kubernetes"],
        ["Python", "FastAPI", "Angular", "MySQL", "Docker"]
    ],
    "Backend Engineer": [
        ["Python", "Django", "PostgreSQL", "Redis", "AWS"],
        ["Java", "Spring Boot", "MySQL", "Kafka", "Microservices"],
        ["Go", "PostgreSQL", "Docker", "Kubernetes", "gRPC"],
        ["Python", "Flask", "SQLAlchemy", "PostgreSQL", "Celery"],
        ["Ruby", "Rails", "PostgreSQL", "Redis", "Sidekiq"]
    ],
    "Frontend Engineer": [
        ["React", "TypeScript", "CSS", "JavaScript", "Redux"],
        ["Vue.js", "TypeScript", "Nuxt.js", "CSS", "Pinia"],
        ["React", "Next.js", "TypeScript", "Tailwind CSS", "GraphQL"],
        ["Angular", "TypeScript", "RxJS", "SCSS", "NgRx"],
        ["Svelte", "TypeScript", "CSS", "JavaScript", "SvelteKit"]
    ],
    "DevOps Engineer": [
        ["Kubernetes", "Docker", "AWS", "Terraform", "Python"],
        ["AWS", "Terraform", "Jenkins", "Docker", "Ansible"],
        ["Azure", "Kubernetes", "Docker", "CI/CD", "PowerShell"],
        ["GCP", "Kubernetes", "Terraform", "GitLab CI", "Python"],
        ["Docker", "Kubernetes", "AWS", "Prometheus", "Grafana"]
    ],
    "Data Engineer": [
        ["Python", "Spark", "Hadoop", "SQL", "Airflow"],
        ["Python", "Kafka", "Snowflake", "dbt", "Airflow"],
        ["Scala", "Spark", "Databricks", "SQL", "Azure"],
        ["Python", "Airflow", "BigQuery", "dbt", "GCP"],
        ["Java", "Spark", "Hive", "Kafka", "AWS"]
    ],
    "Mobile Developer": [
        ["React Native", "JavaScript", "TypeScript", "Redux", "Firebase"],
        ["Flutter", "Dart", "Firebase", "REST APIs", "SQLite"],
        ["Swift", "iOS", "UIKit", "CoreData", "Combine"],
        ["Kotlin", "Android", "Jetpack Compose", "Room", "Retrofit"],
        ["React Native", "TypeScript", "Expo", "GraphQL", "AsyncStorage"]
    ],
    "QA Engineer": [
        ["Selenium", "Python", "Pytest", "CI/CD", "Jenkins"],
        ["Cypress", "JavaScript", "Jest", "TestRail", "Docker"],
        ["JUnit", "Selenium", "Java", "TestNG", "Maven"],
        ["Postman", "REST Assured", "Java", "CI/CD", "Docker"],
        ["Playwright", "TypeScript", "Jest", "GitHub Actions", "Docker"]
    ],
    "Security Engineer": [
        ["Python", "Penetration Testing", "OWASP", "AWS", "Splunk"],
        ["Security Audits", "Python", "Burp Suite", "Wireshark", "Linux"],
        ["Cryptography", "Python", "PKI", "Security Tools", "Compliance"],
        ["Threat Analysis", "Python", "SIEM", "Incident Response", "Forensics"],
        ["AppSec", "Python", "OWASP", "DevSecOps", "Kubernetes"]
    ]
}

STATUSES = ["new", "reviewed", "hired", "rejected"]
STATUS_WEIGHTS = [0.4, 0.35, 0.15, 0.10]  # Probability distribution

INTERNAL_NOTES_TEMPLATES = [
    "Strong technical background",
    "Good culture fit",
    "Excellent communication skills",
    "Referred by senior engineer",
    "Outstanding problem-solving abilities",
    "Innovative approach to challenges",
    "Strong portfolio and projects",
    "Career changer with unique perspective",
    "Solid experience in the domain",
    "Great team player",
    "Leadership potential",
    "Quick learner, adapts well",
    "Attention to detail is impressive",
    "Good work-life balance awareness",
    "",  # Empty notes
    "",
    ""
]

SCORE_CATEGORIES = [
    "Technical Skills",
    "Problem Solving",
    "Communication",
    "Cultural Fit",
    "Experience Level",
    "Code Quality"
]


def generate_random_candidate(index):
    """Generate a random candidate"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{index}@example.com"
    role = random.choice(ROLES)
    skills = random.choice(SKILL_SETS[role])
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
    internal_notes = random.choice(INTERNAL_NOTES_TEMPLATES)
    
    return {
        "name": name,
        "email": email,
        "role_applied": role,
        "skills": skills,
        "status": status,
        "internal_notes": internal_notes
    }


async def seed_database():
    """Seed the database with sample data"""
    print("Starting database seeding...")
    
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if candidates already exist
            result = await db.execute(select(Candidate))
            existing_candidates = result.scalars().all()
            
            if len(existing_candidates) >= 10:
                print(f"Database already has {len(existing_candidates)} candidates. Skipping seed.")
                print("To reseed, delete the database file: backend/candidates.db")
                return
            
            # Get existing reviewers (must exist - created through registration or admin setup)
            result = await db.execute(select(User).where(User.role == "reviewer"))
            reviewers = result.scalars().all()
            
            if not reviewers:
                print("WARNING: No reviewers found in database.")
                print("Scores will not be added. Register reviewer accounts first.")
            
            # Generate and create random candidates
            print(f"Generating {NUM_CANDIDATES} random candidates...")
            created_candidates = []
            
            for i in range(1, NUM_CANDIDATES + 1):
                candidate_data = generate_random_candidate(i)
                
                # Check if candidate with this email already exists
                result = await db.execute(
                    select(Candidate).where(Candidate.email == candidate_data["email"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"  [{i}/{NUM_CANDIDATES}] Skipping {candidate_data['name']} (already exists)")
                    created_candidates.append(existing)
                    continue
                
                candidate = Candidate(
                    id=str(uuid.uuid4()),
                    name=candidate_data["name"],
                    email=candidate_data["email"],
                    role_applied=candidate_data["role_applied"],
                    skills=candidate_data["skills"],
                    status=candidate_data["status"],
                    internal_notes=candidate_data["internal_notes"],
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))
                )
                db.add(candidate)
                created_candidates.append(candidate)
                print(f"  [{i}/{NUM_CANDIDATES}] Created: {candidate.name} - {candidate.role_applied} ({candidate.status})")
            
            await db.commit()
            print(f"\nSuccessfully created {len(created_candidates)} candidates")
            
            # Add some sample scores for reviewed/hired candidates (only if reviewers exist)
            if reviewers:
                print("\nAdding sample scores...")
                score_count = 0
                
                for candidate in created_candidates:
                    if candidate.status in ["reviewed", "hired"]:
                        # Add 2-4 random scores from different reviewers
                        num_scores = random.randint(2, 4)
                        categories_used = random.sample(SCORE_CATEGORIES, min(num_scores, len(SCORE_CATEGORIES)))
                        
                        for category in categories_used:
                            reviewer = random.choice(reviewers)
                            score_value = random.randint(3, 5) if candidate.status == "hired" else random.randint(2, 5)
                            
                            # Check if score already exists
                            result = await db.execute(
                                select(Score).where(
                                    Score.candidate_id == candidate.id,
                                    Score.category == category,
                                    Score.reviewer_id == reviewer.id
                                )
                            )
                            existing_score = result.scalar_one_or_none()
                            
                            if not existing_score:
                                score = Score(
                                    id=str(uuid.uuid4()),
                                    candidate_id=candidate.id,
                                    category=category,
                                    score=score_value,
                                    reviewer_id=reviewer.id,
                                    note=f"{'Excellent' if score_value >= 4 else 'Good'} performance in {category.lower()}",
                                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                                )
                                db.add(score)
                                score_count += 1
                
                await db.commit()
                print(f"Successfully created {score_count} sample scores")
            
            # Print summary
            print("\n" + "="*60)
            print("Database seeding completed successfully!")
            print("="*60)
            
            # Count candidates by status
            status_counts = {}
            for candidate in created_candidates:
                status_counts[candidate.status] = status_counts.get(candidate.status, 0) + 1
            
            print(f"Summary:")
            print(f"  - Total candidates: {len(created_candidates)}")
            for status, count in sorted(status_counts.items()):
                print(f"    - {status.capitalize()}: {count}")
            print(f"  - Total reviewers in system: {len(reviewers)}")
            if reviewers:
                print(f"  - Total scores generated: {score_count}")
            
            print("\nAdmin credentials:")
            print("  Email: admin@techkraft.com | Password: Admin123!")
            print("\nRegister reviewer accounts through:")
            print("  - Frontend UI: http://localhost:5173")
            print("  - API: POST http://localhost:8000/auth/register")
            print("="*60)
            
        except Exception as e:
            print(f"Error seeding database: {str(e)}")
            raise


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TechKraft Candidate Database Seeder")
    print("="*60 + "\n")
    
    try:
        asyncio.run(seed_database())
    except KeyboardInterrupt:
        print("\nSeeding interrupted by user")
    except Exception as e:
        print(f"\nFailed to seed database: {str(e)}")
        sys.exit(1)
