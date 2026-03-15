"""
Quick Commerce Sales & Delivery Insights Dashboard
FastAPI Backend — Main Application Entry Point
Author: Mohd Shaad | Integral University, CSE
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.database import Base, engine
from app.routers import auth, sales, products, outlets, analytics, upload

# ── Create all tables ──────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App instance ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Quick Commerce Dashboard API",
    description=(
        "REST API for analyzing Blinkit Quick Commerce sales data.\n\n"
        "Built with FastAPI + SQLAlchemy + SQLite.\n"
        "Project by **Mohd Shaad**, Integral University — CSE Department."
    ),
    version="1.0.0",
    contact={"name": "Mohd Shaad", "email": "mohdshaad.861@gmail.com"},
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc UI
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ────────────────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/auth",      tags=["Authentication"])
app.include_router(sales.router,     prefix="/api/sales",     tags=["Sales"])
app.include_router(products.router,  prefix="/api/products",  tags=["Products"])
app.include_router(outlets.router,   prefix="/api/outlets",   tags=["Outlets"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(upload.router,    prefix="/api/upload",    tags=["Data Upload"])


# ── Health Check ───────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "project": "Quick Commerce Sales Dashboard",
        "author": "Mohd Shaad",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return JSONResponse({"status": "ok", "version": "1.0.0"})
