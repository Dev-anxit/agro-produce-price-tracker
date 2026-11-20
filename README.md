# Agro Produce Price Tracker 🌾

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![ORM](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![Database](https://img.shields.io/badge/SQLite-3-lightgrey.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/pytest-31%20passed-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

A robust RESTful API and interactive market intelligence service built with Flask, Flask-SQLAlchemy, and SQLite to record, update, analyze, and look up daily market prices of agricultural commodities across Agricultural Produce Market Committees (APMCs).

---

## Table of Contents
- [Architecture & Design](#architecture--design)
- [Tech Stack](#tech-stack)
- [Data Model](#data-model)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Virtual Environment](#installation--virtual-environment)
  - [Database Seeding](#database-seeding)
  - [Running the Application](#running-the-application)
- [Automated Testing](#automated-testing)
- [API Reference](#api-reference)
  - [1. List All Prices (`GET /prices`)](#1-list-all-prices-get-prices)
  - [2. Get Price by ID (`GET /prices/<id>`)](#2-get-price-by-id-get-pricesid)
  - [3. Add Price Record (`POST /prices`)](#3-add-price-record-post-prices)
  - [4. Update Record (`PUT /prices/<id>`)](#4-update-record-put-pricesid)
  - [5. Delete Record (`DELETE /prices/<id>`)](#5-delete-record-delete-pricesid)
  - [6. Latest Price for Crop (`GET /prices/latest`)](#6-latest-price-for-crop-get-priceslatest)
  - [7. Date-Span Average Price (`GET /prices/average`)](#7-date-span-average-price-get-pricesaverage)
- [Interactive Web UI](#interactive-web-ui)
- [Error Handling](#error-handling)
- [Postman / API Test Matrix](#postman--api-test-matrix)
- [Project Structure](#project-structure)

---

## Architecture & Design

The service follows Flask application factory conventions and strict REST principles:
- **Application Factory (`create_app`)**: Allows environment isolation and testing with in-memory SQLite (`sqlite:///:memory:`).
- **Modern SQLAlchemy 2.x Type Mappings**: Model columns utilize typed `Mapped` and `mapped_column` declarations for IDE type-safety and Pylance compatibility.
- **Defensive Validation Pipeline**: Validates required keys, non-empty trimmed strings, strictly positive prices, and `YYYY-MM-DD` calendar dates before executing database mutations.
- **Standardized JSON Error Envelopes**: Global error handlers intercept 400, 404, and 500 status codes, returning uniform JSON objects.

---

## Tech Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.10+ | Core language runtime |
| **Web Framework** | Flask | 3.x | REST API routing and request handling |
| **ORM / Storage** | Flask-SQLAlchemy | 3.x | ORM layer and SQLite integration |
| **Frontend UI** | Vanilla HTML5 / CSS3 / JS | - | Zero-dependency studio interface |
| **Visualizations** | Chart.js | 4.x (CDN) | Interactive commodity trend curves |
| **Test Engine** | pytest | 8.x | Automated unit and integration testing |

---

## Data Model

### `PriceRecord` (`price_records` table)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key, Autoincrement | Unique record identifier |
| `crop_name` | String(100) | Non-Null, Indexed | Commodity name (e.g., `Wheat`, `Rice`, `Tomato`) |
| `market` | String(100) | Non-Null, Indexed | APMC wholesale market (e.g., `Pune APMC`) |
| `price_per_quintal` | Float | Non-Null, Value > 0 | Price in INR per quintal |
| `price_date` | Date | Non-Null, Indexed | Recorded market date (`YYYY-MM-DD`) |
| `created_at` | DateTime | Non-Null, UTC Default | System timestamp of record entry |

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Installation & Virtual Environment

```bash
# Clone the repository
git clone https://github.com/Dev-anxit/agro-produce-price-tracker.git
cd agro-produce-price-tracker

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows

# Install project dependencies
pip install -r requirements.txt
```

### Database Seeding
Populate the SQLite database with 16 realistic APMC produce records:
```bash
python seed.py
```
*Console output:*
```text
Successfully seeded 16 price records into the database.
```

### Running the Application
```bash
python app.py
```
The application server runs locally at: **`http://127.0.0.1:5000`** *(or `5001` if port 5000 is occupied by macOS AirPlay)*.

---

## Automated Testing

The automated test suite in `tests/test_api.py` includes **31 test cases** verifying all positive paths, query filtering, missing payload fields, negative prices, invalid dates, 404 lookups, and global 500 error interception:

```bash
pytest -v
```

*Output:*
```text
============================== 31 passed in 0.26s ==============================
```

---

## API Reference

Base URL: `http://127.0.0.1:5000`

### 1. List All Prices (`GET /prices`)
Retrieve all price records ordered chronologically by latest date. Supports optional query filters.

**Query Parameters:**
- `crop` *(optional)*: Filter by crop name (case-insensitive, e.g. `wheat`)
- `market` *(optional)*: Filter by market name (case-insensitive, e.g. `Pune APMC`)

```bash
curl -X GET "http://127.0.0.1:5000/prices?crop=wheat&market=Pune%20APMC"
```

**Response (`200 OK`):**
```json
[
  {
    "id": 2,
    "crop_name": "Wheat",
    "market": "Pune APMC",
    "price_per_quintal": 2480.0,
    "price_date": "2026-11-15",
    "created_at": "2026-11-20 05:04:43"
  },
  {
    "id": 1,
    "crop_name": "Wheat",
    "market": "Pune APMC",
    "price_per_quintal": 2450.0,
    "price_date": "2026-11-10",
    "created_at": "2026-11-20 05:04:43"
  }
]
```

---

### 2. Get Price by ID (`GET /prices/<id>`)
Retrieve details for a single price entry.

```bash
curl -X GET "http://127.0.0.1:5000/prices/1"
```

**Response (`200 OK`):**
```json
{
  "id": 1,
  "crop_name": "Wheat",
  "market": "Pune APMC",
  "price_per_quintal": 2450.0,
  "price_date": "2026-11-10",
  "created_at": "2026-11-20 05:04:43"
}
```

**Error Response (`404 Not Found`):**
```json
{
  "error": "Price record not found"
}
```

---

### 3. Add Price Record (`POST /prices`)
Create a new daily price entry.

```bash
curl -X POST "http://127.0.0.1:5000/prices" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Soybean",
    "market": "Latur APMC",
    "price_per_quintal": 4850.00,
    "price_date": "2026-11-20"
  }'
```

**Response (`201 Created`):**
```json
{
  "id": 17,
  "crop_name": "Soybean",
  "market": "Latur APMC",
  "price_per_quintal": 4850.0,
  "price_date": "2026-11-20",
  "created_at": "2026-11-20 05:43:22"
}
```

---

### 4. Update Record (`PUT /prices/<id>`)
Update an existing price entry.

```bash
curl -X PUT "http://127.0.0.1:5000/prices/1" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Wheat (Sharbati)",
    "market": "Pune APMC",
    "price_per_quintal": 2650.00,
    "price_date": "2026-11-10"
  }'
```

**Response (`200 OK`):**
```json
{
  "id": 1,
  "crop_name": "Wheat (Sharbati)",
  "market": "Pune APMC",
  "price_per_quintal": 2650.0,
  "price_date": "2026-11-10",
  "created_at": "2026-11-20 05:04:43"
}
```

---

### 5. Delete Record (`DELETE /prices/<id>`)
Remove a record from the ledger.

```bash
curl -X DELETE "http://127.0.0.1:5000/prices/1"
```

**Response (`200 OK`):**
```json
{
  "message": "Price record deleted successfully"
}
```

---

### 6. Latest Price for Crop (`GET /prices/latest`)
Look up the most recently recorded quotation for a specified crop.

```bash
curl -X GET "http://127.0.0.1:5000/prices/latest?crop=Wheat"
```

**Response (`200 OK`):**
```json
{
  "id": 3,
  "crop_name": "Wheat",
  "market": "Nagpur APMC",
  "price_per_quintal": 2510.5,
  "price_date": "2026-11-18",
  "created_at": "2026-11-20 05:04:43"
}
```

---

### 7. Date-Span Average Price (`GET /prices/average`)
Compute the arithmetic mean price per quintal for a crop across an inclusive date boundary.

```bash
curl -X GET "http://127.0.0.1:5000/prices/average?crop=Wheat&from=2026-11-01&to=2026-11-20"
```

**Response (`200 OK`):**
```json
{
  "crop": "Wheat",
  "from": "2026-11-01",
  "to": "2026-11-20",
  "average_price_per_quintal": 2480.17,
  "record_count": 3
}
```

---

## Interactive Web UI

Serving directly from `/`, the integrated **Kisan Mandi Exchange** user interface features:
- **Dual Presentation Views**: Seamlessly switch between a visual **Commodity Card Deck** and a dense **Ledger Table**.
- **Payout Calculator**: Real-time Quintal-to-Kg conversion calculator (`Weight in Kg × Rate / 100`).
- **Interactive Price Curves**: Chart.js visualization plotting multi-crop price movements over time.
- **Slide-in Studio Drawer**: Clean form panel sliding in from the right edge for creating and updating records.
- **One-Click CSV Export**: Download all ledger records directly to `.csv`.

---

## Error Handling

All error responses strictly return JSON envelopes:

| Status Code | Scenario | Sample Payload |
|---|---|---|
| `400 Bad Request` | Missing field, negative price, invalid date | `{"error": "Field 'price_per_quintal' must be greater than 0"}` |
| `404 Not Found` | Unmatched ID or missing commodity record | `{"error": "Price record not found"}` |
| `500 Internal Server Error` | Uncaught server exception | `{"error": "Internal server error"}` |

---

## Postman / API Test Matrix

| # | Action | Method | URL | Payload | Status |
|---|---|:---:|---|---|:---:|
| 1 | List All Records | `GET` | `/prices` | None | `200` |
| 2 | Filter Crop & Market | `GET` | `/prices?crop=Wheat&market=Pune%20APMC` | None | `200` |
| 3 | Single Record Lookup | `GET` | `/prices/1` | None | `200` |
| 4 | Non-existent Record | `GET` | `/prices/999` | None | `404` |
| 5 | Create Record | `POST` | `/prices` | `{"crop_name": "Corn", "market": "Pune APMC", "price_per_quintal": 2100, "price_date": "2026-11-20"}` | `201` |
| 6 | Create (Invalid Price) | `POST` | `/prices` | `{"crop_name": "Corn", "market": "Pune APMC", "price_per_quintal": -5, "price_date": "2026-11-20"}` | `400` |
| 7 | Create (Bad Date) | `POST` | `/prices` | `{"crop_name": "Corn", "market": "Pune APMC", "price_per_quintal": 2100, "price_date": "20-11-2026"}` | `400` |
| 8 | Update Record | `PUT` | `/prices/1` | `{"crop_name": "Wheat", "market": "Pune APMC", "price_per_quintal": 2500, "price_date": "2026-11-10"}` | `200` |
| 9 | Delete Record | `DELETE` | `/prices/1` | None | `200` |
| 10 | Latest Rate Query | `GET` | `/prices/latest?crop=Wheat` | None | `200` |
| 11 | Date Range Mean | `GET` | `/prices/average?crop=Wheat&from=2026-11-01&to=2026-11-20` | None | `200` |

---

## Project Structure

```text
agro-produce-price-tracker/
├── app.py                # Application factory and route handlers
├── models.py             # SQLAlchemy 2.x data model
├── seed.py               # Database seeder (16 sample APMC entries)
├── requirements.txt      # Python dependencies
├── pytest.ini            # Pytest configuration
├── README.md             # Complete documentation
├── .gitignore            # Git exclusions
├── templates/
│   └── index.html        # Interactive Mandi Exchange Web UI
└── tests/
    └── test_api.py       # 31 automated test cases
```
