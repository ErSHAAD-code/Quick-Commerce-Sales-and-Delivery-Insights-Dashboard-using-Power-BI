# Quick Commerce Sales Dashboard — Backend API

**Project by Mohd Shaad | Integral University, CSE**
**Email:** mohdshaad.861@gmail.com

A production-ready REST API backend for the **Blinkit Quick Commerce Sales & Delivery Insights Dashboard**, built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

---

## Tech Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Framework    | FastAPI                 |
| Database     | SQLite (via SQLAlchemy) |
| Auth         | JWT (python-jose)       |
| Passwords    | bcrypt (passlib)        |
| Data Upload  | pandas + openpyxl       |
| Server       | Uvicorn (ASGI)          |

---

## Project Structure

```
qc_backend/
├── app/
│   ├── main.py               ← FastAPI app, router registration
│   ├── core/
│   │   ├── database.py       ← SQLAlchemy engine & session
│   │   └── security.py       ← JWT & password hashing
│   ├── models/
│   │   └── user.py           ← DB models: User, Product, Outlet, SaleRecord
│   ├── schemas/
│   │   └── schemas.py        ← Pydantic request/response models
│   └── routers/
│       ├── auth.py           ← Register, Login, Profile
│       ├── sales.py          ← CRUD for sale records
│       ├── products.py       ← CRUD for products
│       ├── outlets.py        ← CRUD for outlets
│       ├── analytics.py      ← KPIs & chart data
│       └── upload.py         ← CSV / Excel bulk upload
├── data/                     ← SQLite database stored here
├── seed.py                   ← Populate DB with sample data
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed the database with sample data
```bash
python seed.py
```

### 3. Start the server
```bash
uvicorn app.main:app --reload
```

Server runs at: **http://127.0.0.1:8000**

---

## API Documentation

Once running, open:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:**       http://127.0.0.1:8000/redoc

---

## API Endpoints

### Authentication
| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| POST   | `/api/auth/register`  | Create account           |
| POST   | `/api/auth/login`     | Login, get JWT token     |
| GET    | `/api/auth/me`        | Get current user profile |

### Sales
| Method | Endpoint           | Description                       |
|--------|--------------------|-----------------------------------|
| GET    | `/api/sales/`      | List sales (paginated + filtered) |
| GET    | `/api/sales/{id}`  | Get single sale                   |
| POST   | `/api/sales/`      | Create a sale record              |
| DELETE | `/api/sales/{id}`  | Delete a sale (admin only)        |

### Products
| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| GET    | `/api/products/`      | List all products        |
| GET    | `/api/products/types` | Get all product types    |
| GET    | `/api/products/{id}`  | Get single product       |
| POST   | `/api/products/`      | Add a product            |
| PUT    | `/api/products/{id}`  | Update a product         |
| DELETE | `/api/products/{id}`  | Delete (admin only)      |

### Outlets
| Method | Endpoint             | Description         |
|--------|----------------------|---------------------|
| GET    | `/api/outlets/`      | List all outlets    |
| GET    | `/api/outlets/{id}`  | Get single outlet   |
| POST   | `/api/outlets/`      | Add an outlet       |
| PUT    | `/api/outlets/{id}`  | Update an outlet    |
| DELETE | `/api/outlets/{id}`  | Delete (admin only) |

### Analytics (Dashboard Data)
| Method | Endpoint                            | Description                     |
|--------|-------------------------------------|---------------------------------|
| GET    | `/api/analytics/kpi`                | Total Sales, Avg Sales, Ratings |
| GET    | `/api/analytics/sales-by-category`  | Sales by product type (bar chart) |
| GET    | `/api/analytics/sales-by-outlet-type` | Sales by outlet type           |
| GET    | `/api/analytics/sales-by-location`  | Sales by Tier 1/2/3 location    |
| GET    | `/api/analytics/sales-by-fat-content` | Fat content distribution (pie) |
| GET    | `/api/analytics/sales-trend`        | Sales over years (line chart)   |
| GET    | `/api/analytics/top-products`       | Top N best-selling products     |

### Data Upload
| Method | Endpoint            | Description               |
|--------|---------------------|---------------------------|
| POST   | `/api/upload/csv`   | Upload Blinkit CSV file   |
| POST   | `/api/upload/excel` | Upload Blinkit Excel file |

---

## Authentication

All endpoints (except `/api/auth/register` and `/api/auth/login`) require a **Bearer token**.

```bash
# 1. Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=mohdshaad.861@gmail.com&password=shaad123"

# 2. Use token in header
curl http://localhost:8000/api/analytics/kpi \
  -H "Authorization: Bearer <your_token>"
```

---


## Uploading Blinkit Dataset

Download the dataset from **Kaggle: Blinkit Grocery Dataset**, then:

```bash
curl -X POST http://localhost:8000/api/upload/csv \
  -H "Authorization: Bearer <token>" \
  -F "file=@blinkit_data.csv"
```

---

## Future Enhancements

- Connect to PostgreSQL for production deployment
- Add real-time data streaming via WebSockets
- Integrate predictive analytics with scikit-learn
- Deploy on Render / Railway / AWS with Docker
