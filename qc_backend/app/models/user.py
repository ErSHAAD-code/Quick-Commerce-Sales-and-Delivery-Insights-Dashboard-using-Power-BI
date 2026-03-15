"""
Database Models — SQLAlchemy ORM
Tables: User, SaleRecord, Product, Outlet
"""

from sqlalchemy import (
    Column, Integer, Float, String, Boolean,
    DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# ── Enums ──────────────────────────────────────────────────────────────────────
class OutletSizeEnum(str, enum.Enum):
    small = "Small"
    medium = "Medium"
    high = "High"


class OutletTypeEnum(str, enum.Enum):
    grocery = "Grocery Store"
    supermarket1 = "Supermarket Type1"
    supermarket2 = "Supermarket Type2"
    supermarket3 = "Supermarket Type3"


class LocationTierEnum(str, enum.Enum):
    tier1 = "Tier 1"
    tier2 = "Tier 2"
    tier3 = "Tier 3"


class FatContentEnum(str, enum.Enum):
    low_fat = "Low Fat"
    regular = "Regular"


# ── User ───────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active     = Column(Boolean, default=True)
    is_admin      = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.utcnow)


# ── Outlet ─────────────────────────────────────────────────────────────────────
class Outlet(Base):
    __tablename__ = "outlets"

    id                   = Column(Integer, primary_key=True, index=True)
    outlet_identifier    = Column(String(20), unique=True, index=True, nullable=False)
    outlet_establishment_year = Column(Integer, nullable=False)
    outlet_size          = Column(String(20))
    outlet_location_type = Column(String(20))
    outlet_type          = Column(String(50))
    city                 = Column(String(100))

    # Relationship
    sales = relationship("SaleRecord", back_populates="outlet")

    @property
    def age_years(self):
        return datetime.utcnow().year - self.outlet_establishment_year


# ── Product ────────────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    id              = Column(Integer, primary_key=True, index=True)
    item_identifier = Column(String(20), unique=True, index=True, nullable=False)
    item_type       = Column(String(60), nullable=False)
    fat_content     = Column(String(20))
    item_weight     = Column(Float)
    item_mrp        = Column(Float, nullable=False)

    # Relationship
    sales = relationship("SaleRecord", back_populates="product")


# ── Sale Record ────────────────────────────────────────────────────────────────
class SaleRecord(Base):
    __tablename__ = "sale_records"

    id                 = Column(Integer, primary_key=True, index=True)
    product_id         = Column(Integer, ForeignKey("products.id"), nullable=False)
    outlet_id          = Column(Integer, ForeignKey("outlets.id"), nullable=False)
    item_visibility    = Column(Float, default=0.0)
    item_outlet_sales  = Column(Float, nullable=False)
    rating             = Column(Float)
    sale_date          = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="sales")
    outlet  = relationship("Outlet", back_populates="sales")
