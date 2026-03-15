"""
Upload Router — CSV / Excel Data Ingestion
POST /api/upload/csv   — Upload Blinkit CSV dataset
POST /api/upload/excel — Upload Blinkit Excel dataset
"""

import io
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Product, Outlet, SaleRecord
from app.schemas.schemas import UploadResult

router = APIRouter()


# ── Expected CSV columns ───────────────────────────────────────────────────────
REQUIRED_COLUMNS = {
    "Item_Identifier", "Item_Type", "Item_Fat_Content",
    "Item_Weight", "Item_MRP", "Item_Visibility",
    "Outlet_Identifier", "Outlet_Establishment_Year",
    "Outlet_Size", "Outlet_Location_Type", "Outlet_Type",
    "Item_Outlet_Sales",
}


def _normalize_fat_content(val: str) -> str:
    """Normalize fat content values (LF, low fat → Low Fat)."""
    mapping = {
        "lf": "Low Fat", "low fat": "Low Fat",
        "reg": "Regular", "regular": "Regular",
    }
    return mapping.get(str(val).strip().lower(), str(val).strip())


def _process_dataframe(df: pd.DataFrame, db: Session) -> UploadResult:
    """Parse a DataFrame and bulk-insert Products, Outlets, SaleRecords."""
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {', '.join(sorted(missing))}",
        )

    rows_processed = len(df)
    rows_inserted = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            # ── Product ──────────────────────────────────────────────────
            item_id = str(row["Item_Identifier"]).strip()
            product = db.query(Product).filter(Product.item_identifier == item_id).first()
            if not product:
                product = Product(
                    item_identifier=item_id,
                    item_type=str(row["Item_Type"]).strip(),
                    fat_content=_normalize_fat_content(row.get("Item_Fat_Content", "")),
                    item_weight=float(row["Item_Weight"]) if pd.notna(row.get("Item_Weight")) else None,
                    item_mrp=float(row["Item_MRP"]),
                )
                db.add(product)
                db.flush()

            # ── Outlet ───────────────────────────────────────────────────
            outlet_id = str(row["Outlet_Identifier"]).strip()
            outlet = db.query(Outlet).filter(Outlet.outlet_identifier == outlet_id).first()
            if not outlet:
                outlet = Outlet(
                    outlet_identifier=outlet_id,
                    outlet_establishment_year=int(row["Outlet_Establishment_Year"]),
                    outlet_size=str(row.get("Outlet_Size", "")).strip() or None,
                    outlet_location_type=str(row.get("Outlet_Location_Type", "")).strip() or None,
                    outlet_type=str(row.get("Outlet_Type", "")).strip() or None,
                )
                db.add(outlet)
                db.flush()

            # ── Sale Record ───────────────────────────────────────────────
            sale = SaleRecord(
                product_id=product.id,
                outlet_id=outlet.id,
                item_visibility=float(row.get("Item_Visibility", 0.0)),
                item_outlet_sales=float(row["Item_Outlet_Sales"]),
                rating=None,
            )
            db.add(sale)
            rows_inserted += 1

        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
            if len(errors) >= 20:
                errors.append("... too many errors, stopping early.")
                break

    db.commit()

    return UploadResult(
        message="Upload complete",
        rows_processed=rows_processed,
        rows_inserted=rows_inserted,
        errors=errors,
    )


# ── CSV Upload ─────────────────────────────────────────────────────────────────
@router.post("/csv", response_model=UploadResult)
async def upload_csv(
    file: UploadFile = File(..., description="Blinkit dataset CSV file"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Upload a Blinkit sales CSV file.

    The CSV must contain these columns:
    `Item_Identifier, Item_Type, Item_Fat_Content, Item_Weight, Item_MRP,
    Item_Visibility, Outlet_Identifier, Outlet_Establishment_Year,
    Outlet_Size, Outlet_Location_Type, Outlet_Type, Item_Outlet_Sales`
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse CSV: {e}")

    return _process_dataframe(df, db)


# ── Excel Upload ───────────────────────────────────────────────────────────────
@router.post("/excel", response_model=UploadResult)
async def upload_excel(
    file: UploadFile = File(..., description="Blinkit dataset Excel file (.xlsx)"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Upload a Blinkit sales Excel (.xlsx) file."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx / .xls files are accepted")

    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse Excel file: {e}")

    return _process_dataframe(df, db)
