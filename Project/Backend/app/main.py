from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, auth, complaints, firs, stations, users, verification
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Digital FIR Management System API",
    description="Blockchain-backed Digital FIR Management System - BSCS FYP",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(verification.router)
app.include_router(stations.router)
app.include_router(complaints.router)
app.include_router(firs.router)
app.include_router(audit.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "environment": settings.environment}