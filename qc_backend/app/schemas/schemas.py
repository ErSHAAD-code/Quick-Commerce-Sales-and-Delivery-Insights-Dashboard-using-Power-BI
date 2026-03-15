"""
Pydantic Schemas — Request & Response Validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ── Auth Schemas ───────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Mohd Shaad")
    email: EmailStr = Field(..., example="mohdshaad.861@gmail.com")
    password: str = Field(..., min_length=6, example="secret123")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Product Schemas ────────────────────────────────────────────────────────────
class ProductCreate(BaseModel):
    item_identifier: str = Field(..., example="FD001")
    item_type: str = Field(..., example="Fruits and Vegetables")
    fat_content: Optional[str] = Field(None, example="Low Fat")
    item_weight: Optional[float] = Field(None, example=9.3)
    item_mrp: float = Field(..., example=249.99)


class ProductOut(ProductCreate):
    id: int

    class Config:
        from_attributes = True


# ── Outlet Schemas ─────────────────────────────────────────────────────────────
class OutletCreate(BaseModel):
    outlet_identifier: str = Field(..., example="OUT001")
    outlet_establishment_year: int = Field(..., example=2010)
    outlet_size: Optional[str] = Field(None, example="Medium")
    outlet_location_type: Optional[str] = Field(None, example="Tier 1")
    outlet_type: Optional[str] = Field(None, example="Supermarket Type1")
    city: Optional[str] = Field(None, example="Delhi")


class OutletOut(OutletCreate):
    id: int

    class Config:
        from_attributes = True


# ── Sale Schemas ───────────────────────────────────────────────────────────────
class SaleCreate(BaseModel):
    product_id: int
    outlet_id: int
    item_visibility: float = Field(0.0, ge=0.0, le=1.0)
    item_outlet_sales: float = Field(..., gt=0)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)


class SaleOut(BaseModel):
    id: int
    item_outlet_sales: float
    item_visibility: float
    rating: Optional[float]
    sale_date: datetime
    product: ProductOut
    outlet: OutletOut

    class Config:
        from_attributes = True


# ── Analytics Schemas ──────────────────────────────────────────────────────────
class KPISummary(BaseModel):
    total_sales: float
    average_sales: float
    total_items: int
    average_rating: float
    total_outlets: int
    total_products: int


class SalesByCategory(BaseModel):
    item_type: str
    total_sales: float
    item_count: int


class SalesByOutletType(BaseModel):
    outlet_type: str
    total_sales: float
    outlet_count: int


class SalesByLocation(BaseModel):
    location_tier: str
    total_sales: float


class SalesByFatContent(BaseModel):
    fat_content: str
    total_sales: float
    percentage: float


class SalesTrend(BaseModel):
    year: int
    total_sales: float


class TopProduct(BaseModel):
    item_identifier: str
    item_type: str
    total_sales: float
    sale_count: int


# ── Upload Schema ──────────────────────────────────────────────────────────────
class UploadResult(BaseModel):
    message: str
    rows_processed: int
    rows_inserted: int
    errors: List[str] = []
