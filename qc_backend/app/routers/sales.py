"""
Sales Router — CRUD for Sale Records
GET    /api/sales            — List all sales (with filters)
GET    /api/sales/{id}       — Get single sale
POST   /api/sales            — Create a sale record
DELETE /api/sales/{id}       — Delete a sale (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, SaleRecord, Product, Outlet
from app.schemas.schemas import SaleCreate, SaleOut

router = APIRouter()


# ── List Sales ─────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[SaleOut])
def list_sales(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=500, description="Max records to return"),
    outlet_type: Optional[str] = Query(None, description="Filter by outlet type"),
    item_type: Optional[str] = Query(None, description="Filter by product category"),
    min_sales: Optional[float] = Query(None, description="Minimum sales value"),
    max_sales: Optional[float] = Query(None, description="Maximum sales value"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Retrieve paginated sale records with optional filters.

    Filters:
    - **outlet_type**: e.g. `Supermarket Type1`
    - **item_type**: e.g. `Fruits and Vegetables`
    - **min_sales** / **max_sales**: sales value range
    """
    query = db.query(SaleRecord).options(
        joinedload(SaleRecord.product),
        joinedload(SaleRecord.outlet),
    )

    if outlet_type:
        query = query.join(Outlet).filter(Outlet.outlet_type == outlet_type)
    if item_type:
        query = query.join(Product).filter(Product.item_type == item_type)
    if min_sales is not None:
        query = query.filter(SaleRecord.item_outlet_sales >= min_sales)
    if max_sales is not None:
        query = query.filter(SaleRecord.item_outlet_sales <= max_sales)

    return query.offset(skip).limit(limit).all()


# ── Get Single Sale ────────────────────────────────────────────────────────────
@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a single sale record by ID."""
    sale = (
        db.query(SaleRecord)
        .options(joinedload(SaleRecord.product), joinedload(SaleRecord.outlet))
        .filter(SaleRecord.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail=f"Sale #{sale_id} not found")
    return sale


# ── Create Sale ────────────────────────────────────────────────────────────────
@router.post("/", response_model=SaleOut, status_code=201)
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Record a new sale entry."""
    # Validate product and outlet exist
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    outlet = db.query(Outlet).filter(Outlet.id == payload.outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    sale = SaleRecord(**payload.dict())
    db.add(sale)
    db.commit()
    db.refresh(sale)

    # Re-fetch with relationships
    return (
        db.query(SaleRecord)
        .options(joinedload(SaleRecord.product), joinedload(SaleRecord.outlet))
        .filter(SaleRecord.id == sale.id)
        .first()
    )


# ── Delete Sale ────────────────────────────────────────────────────────────────
@router.delete("/{sale_id}", status_code=204)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a sale record. Admin only."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    sale = db.query(SaleRecord).filter(SaleRecord.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    db.delete(sale)
    db.commit()
