"""
Analytics Router — Dashboard KPIs & Chart Data
GET /api/analytics/kpi                  — Summary KPIs
GET /api/analytics/sales-by-category    — Sales grouped by item type
GET /api/analytics/sales-by-outlet-type — Sales grouped by outlet type
GET /api/analytics/sales-by-location    — Sales grouped by location tier
GET /api/analytics/sales-by-fat-content — Fat content distribution
GET /api/analytics/sales-trend          — Sales over years (outlet establishment)
GET /api/analytics/top-products         — Top N best-selling products
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, SaleRecord, Product, Outlet
from app.schemas.schemas import (
    KPISummary, SalesByCategory, SalesByOutletType,
    SalesByLocation, SalesByFatContent, SalesTrend, TopProduct,
)

router = APIRouter()


# ── KPI Summary ────────────────────────────────────────────────────────────────
@router.get("/kpi", response_model=KPISummary)
def get_kpi(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """
    Returns top-level KPIs for the dashboard:
    Total Sales, Average Sales, Total Items, Average Rating,
    Total Outlets, Total Products.
    """
    total_sales  = db.query(func.sum(SaleRecord.item_outlet_sales)).scalar() or 0.0
    avg_sales    = db.query(func.avg(SaleRecord.item_outlet_sales)).scalar() or 0.0
    total_items  = db.query(func.count(SaleRecord.id)).scalar() or 0
    avg_rating   = db.query(func.avg(SaleRecord.rating)).scalar() or 0.0
    total_outlets  = db.query(func.count(Outlet.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar() or 0

    return KPISummary(
        total_sales=round(total_sales, 2),
        average_sales=round(avg_sales, 2),
        total_items=total_items,
        average_rating=round(avg_rating, 2),
        total_outlets=total_outlets,
        total_products=total_products,
    )


# ── Sales by Category ──────────────────────────────────────────────────────────
@router.get("/sales-by-category", response_model=List[SalesByCategory])
def sales_by_category(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Total sales and item count grouped by product category (item_type)."""
    rows = (
        db.query(
            Product.item_type,
            func.sum(SaleRecord.item_outlet_sales).label("total_sales"),
            func.count(SaleRecord.id).label("item_count"),
        )
        .join(SaleRecord, SaleRecord.product_id == Product.id)
        .group_by(Product.item_type)
        .order_by(func.sum(SaleRecord.item_outlet_sales).desc())
        .all()
    )
    return [
        SalesByCategory(item_type=r.item_type, total_sales=round(r.total_sales, 2), item_count=r.item_count)
        for r in rows
    ]


# ── Sales by Outlet Type ───────────────────────────────────────────────────────
@router.get("/sales-by-outlet-type", response_model=List[SalesByOutletType])
def sales_by_outlet_type(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Total sales grouped by outlet type (Grocery / Supermarket variants)."""
    rows = (
        db.query(
            Outlet.outlet_type,
            func.sum(SaleRecord.item_outlet_sales).label("total_sales"),
            func.count(Outlet.id.distinct()).label("outlet_count"),
        )
        .join(SaleRecord, SaleRecord.outlet_id == Outlet.id)
        .group_by(Outlet.outlet_type)
        .order_by(func.sum(SaleRecord.item_outlet_sales).desc())
        .all()
    )
    return [
        SalesByOutletType(
            outlet_type=r.outlet_type or "Unknown",
            total_sales=round(r.total_sales, 2),
            outlet_count=r.outlet_count,
        )
        for r in rows
    ]


# ── Sales by Location Tier ─────────────────────────────────────────────────────
@router.get("/sales-by-location", response_model=List[SalesByLocation])
def sales_by_location(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Total sales grouped by location tier (Tier 1 / 2 / 3)."""
    rows = (
        db.query(
            Outlet.outlet_location_type,
            func.sum(SaleRecord.item_outlet_sales).label("total_sales"),
        )
        .join(SaleRecord, SaleRecord.outlet_id == Outlet.id)
        .group_by(Outlet.outlet_location_type)
        .order_by(func.sum(SaleRecord.item_outlet_sales).desc())
        .all()
    )
    return [
        SalesByLocation(location_tier=r.outlet_location_type or "Unknown", total_sales=round(r.total_sales, 2))
        for r in rows
    ]


# ── Sales by Fat Content ───────────────────────────────────────────────────────
@router.get("/sales-by-fat-content", response_model=List[SalesByFatContent])
def sales_by_fat_content(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Fat content distribution — useful for pie chart visualization."""
    rows = (
        db.query(
            Product.fat_content,
            func.sum(SaleRecord.item_outlet_sales).label("total_sales"),
        )
        .join(SaleRecord, SaleRecord.product_id == Product.id)
        .group_by(Product.fat_content)
        .all()
    )
    grand_total = sum(r.total_sales for r in rows) or 1.0
    return [
        SalesByFatContent(
            fat_content=r.fat_content or "Unknown",
            total_sales=round(r.total_sales, 2),
            percentage=round((r.total_sales / grand_total) * 100, 1),
        )
        for r in rows
    ]


# ── Sales Trend over Years ─────────────────────────────────────────────────────
@router.get("/sales-trend", response_model=List[SalesTrend])
def sales_trend(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """
    Sales aggregated by outlet establishment year.
    Useful for line chart — shows how sales vary across older vs newer outlets.
    """
    rows = (
        db.query(
            Outlet.outlet_establishment_year.label("year"),
            func.sum(SaleRecord.item_outlet_sales).label("total_sales"),
        )
        .join(SaleRecord, SaleRecord.outlet_id == Outlet.id)
        .group_by(Outlet.outlet_establishment_year)
        .order_by(Outlet.outlet_establishment_year)
        .all()
    )
    return [SalesTrend(year=r.year, total_sales=round(r.total_sales, 2)) for r in rows]


# ── Top Products ───────────────────────────────────────────────────────────────
@router.get("/top-products", response_model=List[TopProduct])
def top_products(
    n: int = Query(10, ge=1, le=50, description="Number of top products to return"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return the top N best-selling products by total sales value."""
    rows = (
        db.query(
            Product.item_identifier,
            Product.item_type,
            func.sum(SaleRecord.item_outlet_sales).label("total_sales"),
            func.count(SaleRecord.id).label("sale_count"),
        )
        .join(SaleRecord, SaleRecord.product_id == Product.id)
        .group_by(Product.item_identifier, Product.item_type)
        .order_by(func.sum(SaleRecord.item_outlet_sales).desc())
        .limit(n)
        .all()
    )
    return [
        TopProduct(
            item_identifier=r.item_identifier,
            item_type=r.item_type,
            total_sales=round(r.total_sales, 2),
            sale_count=r.sale_count,
        )
        for r in rows
    ]
