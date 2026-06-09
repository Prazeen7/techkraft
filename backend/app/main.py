from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, candidates
import os

app = FastAPI(title="TechKraft Candidate Scoring API", version="1.0.0")

# Configure CORS - Allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include routers
app.include_router(auth.router)
app.include_router(candidates.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print(" Database initialized")
    print(" CORS enabled for all origins (development mode)")

@app.get("/")
async def root():
    return {"message": "TechKraft Candidate Scoring API", "status": "running"}
