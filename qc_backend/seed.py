"""
Seed Script — Populate DB with Sample Blinkit Data
Run: python seed.py

Creates:
  - 1 admin user
  - 10 outlets (across Tier 1/2/3, various types)
  - 30 products (across all Blinkit categories)
  - 200+ sale records
"""

import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User, Product, Outlet, SaleRecord
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("🌱 Seeding database...")

# ── Admin User ─────────────────────────────────────────────────────────────────
if not db.query(User).filter(User.email == "admin@blinkit.com").first():
    admin = User(
        name="Admin",
        email="admin@blinkit.com",
        hashed_password=hash_password("admin123"),
        is_admin=True,
    )
    db.add(admin)

if not db.query(User).filter(User.email == "mohdshaad.861@gmail.com").first():
    user = User(
        name="Mohd Shaad",
        email="mohdshaad.861@gmail.com",
        hashed_password=hash_password("shaad123"),
        is_admin=False,
    )
    db.add(user)

db.commit()
print("  ✓ Users created")

# ── Outlets ────────────────────────────────────────────────────────────────────
outlets_data = [
    ("OUT001", 2010, "Medium",  "Tier 1", "Supermarket Type1", "Delhi"),
    ("OUT002", 2015, "High",    "Tier 1", "Supermarket Type2", "Mumbai"),
    ("OUT003", 2012, "Small",   "Tier 2", "Grocery Store",     "Lucknow"),
    ("OUT004", 2018, "Medium",  "Tier 2", "Supermarket Type1", "Kanpur"),
    ("OUT005", 2009, "High",    "Tier 1", "Supermarket Type3", "Bangalore"),
    ("OUT006", 2016, "Small",   "Tier 3", "Grocery Store",     "Varanasi"),
    ("OUT007", 2013, "Medium",  "Tier 3", "Supermarket Type1", "Allahabad"),
    ("OUT008", 2020, "High",    "Tier 1", "Supermarket Type2", "Hyderabad"),
    ("OUT009", 2011, "Small",   "Tier 2", "Grocery Store",     "Jaipur"),
    ("OUT010", 2017, "Medium",  "Tier 3", "Supermarket Type1", "Pune"),
]

outlets = []
for o in outlets_data:
    existing = db.query(Outlet).filter(Outlet.outlet_identifier == o[0]).first()
    if not existing:
        outlet = Outlet(
            outlet_identifier=o[0],
            outlet_establishment_year=o[1],
            outlet_size=o[2],
            outlet_location_type=o[3],
            outlet_type=o[4],
            city=o[5],
        )
        db.add(outlet)
        db.flush()
        outlets.append(outlet)
    else:
        outlets.append(existing)

db.commit()
print("  ✓ Outlets created")

# ── Products ───────────────────────────────────────────────────────────────────
products_data = [
    ("FD001", "Fruits and Vegetables", "Low Fat",  None,  49.90),
    ("FD002", "Fruits and Vegetables", "Low Fat",  None,  39.50),
    ("FD003", "Snack Foods",           "Regular",  0.15,  89.99),
    ("FD004", "Snack Foods",           "Low Fat",  0.20, 120.00),
    ("FD005", "Household",             "Regular",  2.50, 199.00),
    ("FD006", "Household",             "Regular",  3.10, 250.00),
    ("FD007", "Frozen Foods",          "Regular",  1.80, 180.00),
    ("FD008", "Frozen Foods",          "Low Fat",  1.50, 160.00),
    ("FD009", "Dairy",                 "Low Fat",  0.50,  55.00),
    ("FD010", "Dairy",                 "Regular",  0.80,  75.00),
    ("FD011", "Canned Foods",          "Regular",  0.80,  95.00),
    ("FD012", "Canned Foods",          "Low Fat",  0.60,  85.00),
    ("FD013", "Baking Goods",          "Regular",  0.40,  60.00),
    ("FD014", "Baking Goods",          "Low Fat",  0.30,  50.00),
    ("FD015", "Breads",                "Low Fat",  0.45,  45.00),
    ("FD016", "Breads",                "Regular",  0.50,  55.00),
    ("FD017", "Beverages",             "Low Fat",  1.20, 110.00),
    ("FD018", "Beverages",             "Regular",  1.50, 130.00),
    ("FD019", "Soft Drinks",           "Regular",  0.35,  40.00),
    ("FD020", "Soft Drinks",           "Regular",  0.40,  45.00),
    ("FD021", "Meat",                  "Regular",  0.90, 350.00),
    ("FD022", "Meat",                  "Low Fat",  1.10, 420.00),
    ("FD023", "Seafood",               "Low Fat",  0.70, 299.00),
    ("FD024", "Breakfast",             "Regular",  0.25,  75.00),
    ("FD025", "Breakfast",             "Low Fat",  0.30,  80.00),
    ("FD026", "Starchy Foods",         "Regular",  1.00,  65.00),
    ("FD027", "Hard Drinks",           "Regular",  None, 500.00),
    ("FD028", "Health and Hygiene",    "Regular",  None, 150.00),
    ("FD029", "Others",                "Regular",  None,  99.00),
    ("FD030", "Others",                "Low Fat",  None,  79.00),
]

products = []
for p in products_data:
    existing = db.query(Product).filter(Product.item_identifier == p[0]).first()
    if not existing:
        product = Product(
            item_identifier=p[0],
            item_type=p[1],
            fat_content=p[2],
            item_weight=p[3],
            item_mrp=p[4],
        )
        db.add(product)
        db.flush()
        products.append(product)
    else:
        products.append(existing)

db.commit()
print("  ✓ Products created")

# ── Sale Records ───────────────────────────────────────────────────────────────
random.seed(42)
sale_count = 0

for _ in range(300):
    product = random.choice(products)
    outlet = random.choice(outlets)
    sale = SaleRecord(
        product_id=product.id,
        outlet_id=outlet.id,
        item_visibility=round(random.uniform(0.01, 0.35), 4),
        item_outlet_sales=round(random.uniform(50.0, 13000.0), 2),
        rating=round(random.uniform(1.0, 5.0), 1),
        sale_date=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
    )
    db.add(sale)
    sale_count += 1

db.commit()
print(f"  ✓ {sale_count} sale records created")

db.close()
print("\n✅ Database seeded successfully!")
print("\nLogin credentials:")
print("  Admin  — admin@blinkit.com       / admin123")
print("  User   — mohdshaad.861@gmail.com / shaad123")
