# TechKraft Candidate Scoring Dashboard

An internal candidate scoring and review dashboard for TechKraft's recruitment workflow. This full-stack application enables reviewers to score candidates across multiple categories and provides AI-generated summaries to assist in the hiring process.

## Architecture

**Backend:** FastAPI (Python 3.11+)  
**Frontend:** React 19 + Vite  
**Database:** SQLite with SQLAlchemy ORM  
**Authentication:** JWT-based with role-based access control  
**Containerization:** Docker + Docker Compose

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Setup & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Prazeen7/techkraft.git
   cd techkraft
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the example file 
   cp .env.example .env
   
   # Edit .env with your values if needed
   ```

3. **Start the application:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Default Credentials

The system creates a default admin account on first startup:
- **Email:** admin@techkraft.com
- **Password:** Admin123!

You can register additional reviewer accounts through the registration page.

### Seed Sample Data (Optional)

To populate the database with 50 random sample candidates:

**Windows PowerShell:**
```powershell
cd backend
python seed_data.py
```

**Linux/Mac:**
```bash
cd backend
python seed_data.py
```

This will create:
- 50 randomly generated candidates with diverse names, roles, skills, and statuses
- Random scores for reviewed/hired candidates (if reviewers exist in the system)
- Realistic distribution: ~40% new, ~35% reviewed, ~15% hired, ~10% rejected

**Note:** The script only creates candidates, not reviewer accounts. Register reviewers through the UI or API first if you want sample scores.

### Reset Database (Delete Existing Data)

To delete all existing data and start fresh:

**Windows PowerShell:**
```powershell
# Stop the application first
docker-compose down

# Delete the database file
Remove-Item backend\candidates.db -ErrorAction SilentlyContinue

# Restart and the database will be recreated
docker-compose up --build
```

**Linux/Mac:**
```bash
# Stop the application first
docker-compose down

# Delete the database file
rm -f backend/candidates.db

# Restart and the database will be recreated
docker-compose up --build
```

After reset, the default admin account will be automatically recreated. Then you can run the seed script to add sample candidates.

---

## API Examples

### Authentication

**Register a new reviewer:**

Linux/Mac:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "reviewer@techkraft.com",
    "password": "SecurePass123!",
    "full_name": "Jane Reviewer"
  }'
```

Windows PowerShell:
```powershell
curl.exe -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"reviewer@techkraft.com\", \"password\": \"SecurePass123!\", \"full_name\": \"Jane Reviewer\"}'
```

Or using Invoke-RestMethod (PowerShell):
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/auth/register" -Method Post -ContentType "application/json" -Body (@{
  email = "reviewer@techkraft.com"
  password = "SecurePass123!"
  full_name = "Jane Reviewer"
} | ConvertTo-Json)
```

**Login:**

Linux/Mac:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@techkraft.com",
    "password": "Admin123!"
  }'
```

Windows PowerShell:
```powershell
curl.exe -X POST http://localhost:8000/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"admin@techkraft.com\", \"password\": \"Admin123!\"}'
```

Or using Invoke-RestMethod (PowerShell):
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@techkraft.com"
  password = "Admin123!"
} | ConvertTo-Json)

# Store the token for later use
$token = $response.access_token
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "email": "admin@techkraft.com",
    "role": "admin",
    "full_name": "Admin User"
  }
}
```

### Candidates

**Create a new candidate:**

Linux/Mac:
```bash
curl -X POST http://localhost:8000/candidates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role_applied": "Full Stack Engineer",
    "skills": ["Python", "React", "FastAPI", "Docker"],
    "internal_notes": "Referred by senior engineer"
  }'
```

Windows PowerShell:
```powershell
curl.exe -X POST http://localhost:8000/candidates `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{\"name\": \"John Doe\", \"email\": \"john.doe@example.com\", \"role_applied\": \"Full Stack Engineer\", \"skills\": [\"Python\", \"React\", \"FastAPI\", \"Docker\"], \"internal_notes\": \"Referred by senior engineer\"}'
```

Or using Invoke-RestMethod (PowerShell):
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/candidates" -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body (@{
    name = "John Doe"
    email = "john.doe@example.com"
    role_applied = "Full Stack Engineer"
    skills = @("Python", "React", "FastAPI", "Docker")
    internal_notes = "Referred by senior engineer"
  } | ConvertTo-Json)
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role_applied": "Full Stack Engineer",
  "status": "new",
  "skills": ["Python", "React", "FastAPI", "Docker"],
  "internal_notes": "Referred by senior engineer",
  "created_at": "2026-06-09T18:30:00Z"
}
```

**List candidates with filters:**

Linux/Mac:
```bash
# Get all candidates (first page)
curl http://localhost:8000/candidates?page=1&page_size=20

# Filter by status
curl http://localhost:8000/candidates?status=new&page=1&page_size=20

# Filter by role
curl http://localhost:8000/candidates?role_applied=Full%20Stack%20Engineer&page=1&page_size=20

# Filter by skill
curl http://localhost:8000/candidates?skill=Python&page=1&page_size=20

# Search by keyword
curl http://localhost:8000/candidates?keyword=react&page=1&page_size=20

# Combine filters
curl "http://localhost:8000/candidates?status=reviewed&role_applied=Backend%20Engineer&skill=Python&page=1&page_size=10"
```

Windows PowerShell:
```powershell
# Get all candidates (first page)
curl.exe "http://localhost:8000/candidates?page=1&page_size=20"

# Filter by status
curl.exe "http://localhost:8000/candidates?status=new&page=1&page_size=20"

# Filter by role
curl.exe "http://localhost:8000/candidates?role_applied=Full%20Stack%20Engineer&page=1&page_size=20"

# Filter by skill
curl.exe "http://localhost:8000/candidates?skill=Python&page=1&page_size=20"

# Search by keyword
curl.exe "http://localhost:8000/candidates?keyword=react&page=1&page_size=20"

# Combine filters
curl.exe "http://localhost:8000/candidates?status=reviewed&role_applied=Backend%20Engineer&skill=Python&page=1&page_size=10"
```

Or using Invoke-RestMethod (PowerShell):
```powershell
# Get all candidates with filters
Invoke-RestMethod -Uri "http://localhost:8000/candidates" -Method Get `
  -Body @{
    status = "reviewed"
    role_applied = "Backend Engineer"
    skill = "Python"
    page = 1
    page_size = 10
  }
```

**Get candidate details:**

Linux/Mac:
```bash
curl http://localhost:8000/candidates/{candidate_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Windows PowerShell:
```powershell
curl.exe http://localhost:8000/candidates/{candidate_id} `
  -H "Authorization: Bearer YOUR_TOKEN"

# Or with Invoke-RestMethod
Invoke-RestMethod -Uri "http://localhost:8000/candidates/{candidate_id}" `
  -Headers @{ Authorization = "Bearer $token" }
```

**Submit a score:**

Linux/Mac:
```bash
curl -X POST http://localhost:8000/candidates/{candidate_id}/scores \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Technical Skills",
    "score": 5,
    "note": "Excellent problem-solving abilities"
  }'
```

Windows PowerShell:
```powershell
curl.exe -X POST http://localhost:8000/candidates/{candidate_id}/scores `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{\"category\": \"Technical Skills\", \"score\": 5, \"note\": \"Excellent problem-solving abilities\"}'

# Or with Invoke-RestMethod
Invoke-RestMethod -Uri "http://localhost:8000/candidates/{candidate_id}/scores" -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body (@{
    category = "Technical Skills"
    score = 5
    note = "Excellent problem-solving abilities"
  } | ConvertTo-Json)
```

**Generate AI summary:**

Linux/Mac:
```bash
curl -X POST http://localhost:8000/candidates/{candidate_id}/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Windows PowerShell:
```powershell
curl.exe -X POST http://localhost:8000/candidates/{candidate_id}/summary `
  -H "Authorization: Bearer YOUR_TOKEN"

# Or with Invoke-RestMethod
Invoke-RestMethod -Uri "http://localhost:8000/candidates/{candidate_id}/summary" -Method Post `
  -Headers @{ Authorization = "Bearer $token" }
```

**Stream score updates (SSE - Stretch Goal):**

Linux/Mac:
```bash
curl -N http://localhost:8000/candidates/{candidate_id}/stream \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Windows PowerShell:
```powershell
curl.exe -N http://localhost:8000/candidates/{candidate_id}/stream `
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Admin-Only Endpoints

**Update internal notes:**

Linux/Mac:
```bash
curl -X PUT http://localhost:8000/candidates/{candidate_id}/internal-notes \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "internal_notes": "Strong cultural fit, recommend proceeding to final round"
  }'
```

Windows PowerShell:
```powershell
curl.exe -X PUT http://localhost:8000/candidates/{candidate_id}/internal-notes `
  -H "Authorization: Bearer ADMIN_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{\"internal_notes\": \"Strong cultural fit, recommend proceeding to final round\"}'

# Or with Invoke-RestMethod
Invoke-RestMethod -Uri "http://localhost:8000/candidates/{candidate_id}/internal-notes" -Method Put `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body (@{
    internal_notes = "Strong cultural fit, recommend proceeding to final round"
  } | ConvertTo-Json)
```

---

## Database Schema

### Candidates Table
- `id` (String, PK): UUID
- `name` (String): Full name
- `email` (String, Unique, Indexed): Contact email
- `role_applied` (String, Indexed): Position
- `status` (String, Indexed): new | reviewed | hired | rejected
- `skills` (JSON): Array of skills
- `internal_notes` (Text): Admin-only notes
- `created_at` (DateTime): Timestamp
- `updated_at` (DateTime): Timestamp
- `deleted_at` (DateTime): Soft delete timestamp

**Indexes:** `email`, `role_applied`, `status`

### Scores Table
- `id` (String, PK): UUID
- `candidate_id` (String, Indexed, FK): Reference to candidate
- `category` (String): Score category
- `score` (Integer): 1-5 rating
- `reviewer_id` (String, Indexed, FK): Reference to user
- `note` (Text): Optional reviewer comment
- `created_at` (DateTime): Timestamp
- `updated_at` (DateTime): Timestamp

**Indexes:** `candidate_id`, `reviewer_id`

### Users Table
- `id` (String, PK): UUID
- `email` (String, Unique, Indexed): Login email
- `password_hash` (String): Bcrypt hashed password
- `role` (String): reviewer | admin
- `full_name` (String): Display name
- `is_active` (Boolean): Account status
- `created_at` (DateTime): Timestamp

**Indexes:** `email`

---

## Role-Based Access Control

### Reviewer Role
- View all candidates
- Create new candidates
- Submit scores for any candidate
- View only their own scores
- Cannot view internal notes
- Cannot see scores from other reviewers

### Admin Role
- All reviewer permissions
- Create new candidates
- View all scores from all reviewers
- View and edit internal notes
- Full visibility across the system

**Security Features:**
- JWT-based authentication with secure token handling
- Role is **never** accepted from client during registration (hardcoded to "reviewer")
- Passwords hashed with bcrypt
- Database queries filtered by role automatically
- Admin-only endpoints protected by role checks

---

## Testing

Run the test suite:

```bash
# From the backend directory
cd backend
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
```

**Test Coverage:**
- API endpoint tests (candidate creation, listing, scoring)
- Authentication enforcement (role-based access control)
- Score visibility rules (reviewers see only their scores)
- Admin-only endpoint protection

---

## Bugs & Issues Encountered During Development

### 1. Git Virtual Environment Tracking Issue

**Bug:** The virtual environment folder (recru/) kept being added to git staging even after adding to .gitignore.

**Root Cause:** Files already tracked by Git aren't affected by .gitignore - they must be removed from tracking first.

**Solution:** 
```bash
git rm -r --cached recru/
```
Then updated .gitignore with proper path patterns. This removed the folder from git's index while keeping it locally.

---

### 2. Database Filtering Bug (Assignment Debugging Signal)

**Bug:** The provided code example loaded ALL candidates into memory then filtered in Python, causing performance issues at scale:

```python
def search_candidates(status: str, keyword: str, page: int, page_size: int):
    all_candidates = db.execute("SELECT * FROM candidates").fetchall()
    filtered = [c for c in all_candidates if c["status"] == status]
    # ... also filter by keyword in Python ...
    offset = (page - 1) * page_size
    return filtered[offset : offset + page_size]
```

**Why It Matters at Scale:**
- 100,000 candidates = ~100MB transferred from DB
- O(n) filtering in Python vs O(log n) indexed DB lookups
- Database indexes completely wasted
- Memory exhaustion risk with large datasets

**Solution:** Implemented database-level filtering using SQLAlchemy queries with proper where() clauses before pagination:

```python
async def search_candidates(status: str, keyword: str, page: int, page_size: int):
    offset = (page - 1) * page_size
    query = select(Candidate).where(Candidate.deleted_at.is_(None))
    
    if status:
        query = query.where(Candidate.status == status)
    
    if keyword:
        query = query.where(
            or_(
                Candidate.name.ilike(f"%{keyword}%"),
                Candidate.email.ilike(f"%{keyword}%")
            )
        )
    
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()
```

This approach only loads requested records, utilizes database indexes, and maintains constant memory usage regardless of table size.

---

### 3. Skill Filter Not Working with Partial Matches

**Bug:** Skill filter only showed results after typing the complete word, not partial matches like "Pyt" matching "Python".

**Solution:** Changed skill filtering from exact match to partial match using case-insensitive substring matching:

```python
# Before: exact match
if skill in candidate.skills

# After: partial match
if any(skill.lower() in s.lower() for s in candidate.skills)
```

---

### 4. Registration Success Redirect Issue

**Bug:** After registration, users were automatically logged in instead of being redirected to login page, which was confusing UX.

**Solution:** Modified registration flow to only create the account, show success message, and switch to login mode after 2 seconds:

```javascript
setMessage('Registration successful! Redirecting to login...');
setTimeout(() => {
  setIsLogin(true);
  setMessage('');
}, 2000);
```

---

### 5. Password Validation Error (422)

**Bug:** Registration failed with 422 Unprocessable Entity error when password was shorter than 6 characters, but frontend didn't show why.

**Solution:** Added frontend validation to check password length before submitting:

```javascript
if (formData.password.length < 6) {
  setError('Password must be at least 6 characters long');
  return;
}
```

---

### 6. CORS Policy Blocking Requests

**Bug:** Browser blocked requests with error: "No 'Access-Control-Allow-Origin' header is present on the requested resource."

**Solution:** Configured CORS middleware in FastAPI main.py:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 7. Missing /health Endpoint

**Bug:** Test for /health endpoint failed with 404 Not Found.

**Solution:** Added health check endpoint to main.py:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### 8. Node.js Version Incompatibility in Docker

**Bug:** Docker container failed to build because Vite 6.0 required Node.js 20.19+ but Dockerfile used Node.js 18.

**Error Message:** "The engine 'node' is incompatible with this module."

**Solution:** Updated frontend/Dockerfile:

```dockerfile
# Before
FROM node:18-alpine

# After
FROM node:20-alpine
```

---

### 9. Module Import Error in Tests

**Bug:** `ModuleNotFoundError: No module named 'app'` when running pytest from backend directory.

**Solution:** Set PYTHONPATH environment variable before running tests:

```bash
# From project root
PYTHONPATH=backend pytest backend/tests/

# Or run from project root
pytest backend/tests/
```

---

### 10. DATABASE_URL None Type Error

**Bug:** `TypeError: argument of type 'NoneType' is not iterable` because .env file wasn't being loaded in test environment.

**Solution:** Created .env file in backend directory with proper configuration:

```bash
DATABASE_URL=sqlite+aiosqlite:///./candidates.db
SECRET_KEY=test-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### 11. Soft Delete Not Excluding Archived Candidates

**Bug:** Archived candidates still appeared in candidate list even though deleted_at was set.

**Solution:** Added filter to all query operations:

```python
query = select(Candidate).where(Candidate.deleted_at.is_(None))
```

This ensures soft-deleted (archived) candidates are excluded from all listings.

---

## Architecture Decision Records (ADRs)

### ADR 1: FastAPI over Flask/Django

**Context:**  
Needed to choose a Python web framework for building a modern API with async capabilities, automatic API documentation, and strong typing support.

**Decision:**  
Selected FastAPI as the backend framework.

**Rationale:**
- **Async/Await Native:** Built-in support for async operations critical for the AI summary endpoint and SSE streaming
- **Automatic OpenAPI Docs:** Interactive API documentation generated automatically at `/docs`
- **Pydantic Integration:** Strong typing with automatic validation reduces bugs
- **Performance:** One of the fastest Python frameworks, comparable to Node.js
- **Modern Standards:** Built for Python 3.7+ with type hints throughout

**Trade-offs:**
- Gained: Better performance, built-in docs, type safety
- Accepted: Smaller ecosystem than Django, team needs to learn async patterns
- Accepted: Less "batteries included" than Django (no built-in admin panel)

**Alternatives Considered:**
- Django: Too heavyweight for an API-only service, ORM limitations with async
- Flask: No native async support, requires more boilerplate

---

### ADR 2: SQLite with Soft Deletes

**Context:**  
Needed a database solution for development/demo with a strategy for handling candidate deletions while maintaining data integrity and audit trails.

**Decision:**  
Used SQLite with SQLAlchemy ORM and implemented soft deletes via a `deleted_at` timestamp column.

**Rationale:**
- **Zero Configuration:** SQLite requires no separate database server for demo/development
- **Data Preservation:** Soft deletes maintain referential integrity (scores still reference candidates)
- **Audit Trail:** Can track when and why candidates were archived
- **Reversibility:** "Deleted" candidates can be restored if needed
- **Compliance:** Maintains historical data for legal/reporting requirements
- **Query Filtering:** All queries automatically filter out `deleted_at IS NOT NULL`

**Trade-offs:**
- Gained: Data safety, audit capability, easy recovery
- Accepted: Queries must always filter `deleted_at`, disk space not reclaimed
- Accepted: SQLite not suitable for production (would migrate to PostgreSQL)

**Implementation:**
```python
# Soft delete
candidate.deleted_at = datetime.utcnow()

# All queries filter deleted records
query = select(Candidate).where(Candidate.deleted_at.is_(None))
```

**Production Migration Path:**  
SQLite → PostgreSQL with connection pooling, same SQLAlchemy models work with minimal changes.

---

### ADR 3: JWT Authentication with Role Hardcoding

**Context:**  
Needed secure authentication with role-based access control. Critical security requirement: prevent privilege escalation during registration.

**Decision:**  
Implemented JWT-based authentication with role **always** hardcoded to "reviewer" on registration, never accepting role from client input.

**Rationale:**
- **Security First:** Prevents attackers from registering as admin by sending `{"role": "admin"}`
- **Stateless:** JWT tokens enable horizontal scaling without session storage
- **Standard:** Industry-standard approach, good library support
- **Explicit Admin Creation:** Admin accounts only created through secure channels (startup script, CLI)

**Trade-offs:**
- Gained: Protection against privilege escalation, stateless auth
- Accepted: Tokens can't be revoked without additional infrastructure (refresh token blacklist)
- Accepted: Admin creation requires manual process or special tooling

**Security Implementation:**
```python
# Registration endpoint - role is NEVER from client
@router.post("/auth/register")
async def register(user_data: UserCreate):
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="reviewer",  # HARDCODED - never trust client
        full_name=user_data.full_name
    )
```

**Admin Creation:**
- Environment variable on startup creates first admin
- Future: CLI command for creating additional admins
- Never exposed through public API

---

## Learning Reflection

**What I Tried for the First Time:**

This was my first time implementing **Server-Sent Events (SSE)** for real-time score streaming. The `/candidates/{id}/stream` endpoint uses SSE to push score updates to the frontend as they're created by other reviewers. The challenge was managing long-lived connections in FastAPI and handling proper cleanup on disconnect. I learned that SSE is simpler than WebSockets for unidirectional server→client updates and worked well for this use case.

**What I'd Explore with More Time:**

Given additional time, I would implement **comprehensive integration tests using pytest fixtures** to test the full user journey (registration → login → scoring → AI summary) and add **frontend unit tests with React Testing Library**. I'd also explore replacing the mock AI endpoint with an actual integration to open source AI models to demonstrate proper async LLM integration with proper error handling and timeout management. Additionally, implementing **WebSocket-based real-time notifications** (e.g., "New candidate added", "Score submitted") would enhance the collaborative review experience.

Another area I'd invest in is **database migration tooling** using Alembic to enable safe schema evolution in production, and **comprehensive logging/monitoring** with structured logs to track API performance and user actions for debugging.

---

## Project Structure

```
techkraft/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI app initialization
│   │   ├── database.py          # Database connection & session
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication utilities
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   ├── routers/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   └── candidates.py    # Candidate endpoints
│   │   └── services/
│   │       └── candidate_service.py  # Business logic
│   └── tests/
│       └── test_api.py          # API tests
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx             # App entry point
        ├── App.jsx              # Root component
        ├── api/
        │   └── client.js        # API client
        ├── components/
        │   ├── FilterBar.jsx    # Search & filter UI
        │   ├── Pagination.jsx   # Pagination controls
        │   ├── ScoreForm.jsx    # Score submission form
        │   ├── ScoresList.jsx   # Score display
        │   ├── AISummary.jsx    # AI summary UI
        │   └── InternalNotes.jsx # Admin notes panel
        └── pages/
            ├── Login.jsx        # Login page
            ├── CandidateList.jsx # Candidate listing
            └── CandidateDetail.jsx # Candidate details
```

---

## Security & Responsibility Checklist

- **No Credentials Committed:** Real secrets in `.env` (gitignored), examples in `.env.example`
- **Port Consistency:** README ports match `docker-compose.yml` (8000, 5173)
- **Role Security:** Registration hardcodes role to "reviewer", never accepts from client
- **Soft Deletes:** Candidates use `deleted_at` timestamp, never hard deleted
- **Loading States:** AI summary shows loading spinner and error handling
- **CORS Configuration:** Restricted to frontend origin only
- **Password Hashing:** Bcrypt with proper salt rounds
- **Input Validation:** Pydantic schemas validate all API inputs
- **SQL Injection Protection:** SQLAlchemy ORM prevents SQL injection

---

## Deployment Notes

**For Production Deployment:**

1. **Database:** Migrate to PostgreSQL
   ```python
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
   ```

2. **Environment Variables:** Use secrets manager (AWS Secrets Manager, Azure Key Vault)

3. **CORS:** Update allowed origins to production domain

4. **HTTPS:** Terminate SSL at load balancer or reverse proxy

5. **Rate Limiting:** Add rate limiting middleware to prevent abuse

6. **Logging:** Configure structured logging (JSON) with log aggregation

7. **Monitoring:** Add health checks, metrics (Prometheus), and alerting

---

## License

This is an internal tool developed for TechKraft Inc. recruitment workflow.

---

## Developer

Built as a take-home assignment for TechKraft Inc. Full Stack Engineer (Mid) position.

**Technologies Used:**  
FastAPI • React • SQLAlchemy • JWT • Docker • Vite • SQLite • Pydantic • Axios
