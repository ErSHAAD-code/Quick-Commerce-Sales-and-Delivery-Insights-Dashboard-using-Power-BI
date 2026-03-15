"""
Products Router — CRUD for Products
GET    /api/products         — List all products
GET    /api/products/{id}    — Get single product
POST   /api/products         — Add a product
PUT    /api/products/{id}    — Update a product
DELETE /api/products/{id}    — Delete a product (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Product
from app.schemas.schemas import ProductCreate, ProductOut

router = APIRouter()


@router.get("/", response_model=List[ProductOut])
def list_products(
    skip: int = 0,
    limit: int = Query(100, le=1000),
    item_type: Optional[str] = None,
    fat_content: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all products with optional filtering by type or fat content."""
    q = db.query(Product)
    if item_type:
        q = q.filter(Product.item_type.ilike(f"%{item_type}%"))
    if fat_content:
        q = q.filter(Product.fat_content == fat_content)
    return q.offset(skip).limit(limit).all()


@router.get("/types", response_model=List[str])
def get_product_types(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Return all distinct product categories / item types."""
    rows = db.query(Product.item_type).distinct().all()
    return [r[0] for r in rows if r[0]]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    existing = db.query(Product).filter(Product.item_identifier == payload.item_identifier).first()
    if existing:
        raise HTTPException(status_code=409, detail="Product identifier already exists")

    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
