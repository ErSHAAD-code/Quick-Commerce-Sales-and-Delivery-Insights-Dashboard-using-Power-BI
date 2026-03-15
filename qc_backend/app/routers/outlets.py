"""
Outlets Router — CRUD for Outlets
GET    /api/outlets          — List all outlets
GET    /api/outlets/{id}     — Get single outlet
POST   /api/outlets          — Add an outlet
PUT    /api/outlets/{id}     — Update an outlet
DELETE /api/outlets/{id}     — Delete an outlet (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Outlet
from app.schemas.schemas import OutletCreate, OutletOut

router = APIRouter()


@router.get("/", response_model=List[OutletOut])
def list_outlets(
    skip: int = 0,
    limit: int = Query(100, le=500),
    outlet_type: Optional[str] = None,
    location_type: Optional[str] = None,
    outlet_size: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all outlets. Filter by type, location tier, or size."""
    q = db.query(Outlet)
    if outlet_type:
        q = q.filter(Outlet.outlet_type == outlet_type)
    if location_type:
        q = q.filter(Outlet.outlet_location_type == location_type)
    if outlet_size:
        q = q.filter(Outlet.outlet_size == outlet_size)
    return q.offset(skip).limit(limit).all()


@router.get("/{outlet_id}", response_model=OutletOut)
def get_outlet(outlet_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return outlet


@router.post("/", response_model=OutletOut, status_code=201)
def create_outlet(payload: OutletCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    existing = db.query(Outlet).filter(Outlet.outlet_identifier == payload.outlet_identifier).first()
    if existing:
        raise HTTPException(status_code=409, detail="Outlet identifier already exists")

    outlet = Outlet(**payload.dict())
    db.add(outlet)
    db.commit()
    db.refresh(outlet)
    return outlet


@router.put("/{outlet_id}", response_model=OutletOut)
def update_outlet(
    outlet_id: int,
    payload: OutletCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(outlet, key, value)

    db.commit()
    db.refresh(outlet)
    return outlet


@router.delete("/{outlet_id}", status_code=204)
def delete_outlet(outlet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    db.delete(outlet)
    db.commit()
