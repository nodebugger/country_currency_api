# Country Currency & Exchange API

A RESTful API that fetches country data and exchange rates from external APIs, stores them in a MySQL database, and provides CRUD operations with filtering and sorting capabilities.

## Features

- Fetch and cache country data with currency information
- Retrieve exchange rates and compute estimated GDP
- Filter countries by region or currency
- Sort countries by estimated GDP
- Generate summary images with top countries
- Full CRUD operations on country data

## Prerequisites

- Python 3.8+
- MySQL Server running locally or remotely
- pip (Python package manager)

## Installation

### 1. Clone the repository

```bash
cd country_currency_api
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up MySQL Database

Create a MySQL database:

```sql
CREATE DATABASE countries_db;
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/countries_db
COUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD
RANDOM_MIN=1000
RANDOM_MAX=2000
PORT=8000
```

**Important:** Replace `root` and `password` with your MySQL credentials.

### 6. Run the application

```bash
uvicorn app.main:app --reload --port 8000
```

Or if you have a main.py in the root:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Refresh Country Data

**POST** `/countries/refresh`

Fetches all countries and exchange rates from external APIs, then caches them in the database.

**Response:**
```json
{
  "message": "Refreshed",
  "total_countries": 250,
  "image": "cache/summary.png"
}
```

**Error Responses:**
- `503` - External data source unavailable

---

### 2. Get All Countries

**GET** `/countries`

Retrieve all countries from the database with optional filters and sorting.

**Query Parameters:**
- `region` (optional): Filter by region (e.g., `Africa`, `Europe`)
- `currency` (optional): Filter by currency code (e.g., `NGN`, `USD`)
- `sort` (optional): Sort results (`gdp_desc` for descending GDP)

**Example:**
```bash
GET /countries?region=Africa&sort=gdp_desc
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1600.23,
    "estimated_gdp": 25767448125.2,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-22T18:00:00Z"
  }
]
```

---

### 3. Get Single Country

**GET** `/countries/{name}`

Retrieve a specific country by name (case-insensitive).

**Example:**
```bash
GET /countries/Nigeria
```

**Response:**
```json
{
  "id": 1,
  "name": "Nigeria",
  "capital": "Abuja",
  "region": "Africa",
  "population": 206139589,
  "currency_code": "NGN",
  "exchange_rate": 1600.23,
  "estimated_gdp": 25767448125.2,
  "flag_url": "https://flagcdn.com/ng.svg",
  "last_refreshed_at": "2025-10-22T18:00:00Z"
}
```

**Error Responses:**
- `404` - Country not found

---

### 4. Delete Country

**DELETE** `/countries/{name}`

Delete a country record by name (case-insensitive).

**Example:**
```bash
DELETE /countries/Nigeria
```

**Response:**
- `204 No Content` on success

**Error Responses:**
- `404` - Country not found

---

### 5. Get Status

**GET** `/status`

Show total countries and last refresh timestamp.

**Response:**
```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-22T18:00:00Z"
}
```

---

### 6. Get Summary Image

**GET** `/countries/image`

Serve the generated summary image containing:
- Total number of countries
- Top 5 countries by estimated GDP
- Last refresh timestamp

**Response:**
- PNG image file

**Error Responses:**
- `404` - Summary image not found (run `/countries/refresh` first)

---

## Data Model

### Country Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | Primary key |
| `name` | string | Yes | Country name |
| `capital` | string | No | Capital city |
| `region` | string | No | Geographic region |
| `population` | int | Yes | Population count |
| `currency_code` | string | No | ISO currency code (e.g., NGN, USD) |
| `exchange_rate` | float | No | Exchange rate relative to USD |
| `estimated_gdp` | float | No | Computed: population × random(1000-2000) ÷ exchange_rate |
| `flag_url` | string | No | URL to country flag image |
| `last_refreshed_at` | string | Auto | ISO 8601 timestamp |

## Currency Handling

- If a country has multiple currencies, only the first is stored
- If a country has no currencies:
  - `currency_code` = `null`
  - `exchange_rate` = `null`
  - `estimated_gdp` = `0`
- If currency code is not found in exchange rates API:
  - `exchange_rate` = `null`
  - `estimated_gdp` = `null`

## Error Handling

All errors return JSON responses:

```json
{
  "error": "Error type",
  "details": "Additional information"
}
```

**Status Codes:**
- `400` - Bad Request (validation failed)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (external API failure)

## Testing Examples

### Using cURL

```bash
# Refresh data
curl -X POST http://localhost:8000/countries/refresh

# Get all African countries
curl "http://localhost:8000/countries?region=Africa"

# Get countries using NGN currency
curl "http://localhost:8000/countries?currency=NGN"

# Get countries sorted by GDP
curl "http://localhost:8000/countries?sort=gdp_desc"

# Get specific country
curl http://localhost:8000/countries/Nigeria

# Delete country
curl -X DELETE http://localhost:8000/countries/Nigeria

# Get status
curl http://localhost:8000/status

# Download summary image
curl http://localhost:8000/countries/image --output summary.png
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Refresh data
response = requests.post(f"{BASE_URL}/countries/refresh")
print(response.json())

# Get countries
countries = requests.get(f"{BASE_URL}/countries?region=Africa")
print(countries.json())

# Get status
status = requests.get(f"{BASE_URL}/status")
print(status.json())
```

## Project Structure

```
country_currency_api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── routes.py        # API endpoints
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── services.py      # Business logic & external API calls
│   ├── database.py      # Database connection
│   ├── config.py        # Configuration management
│   ├── utils.py         # Helper functions
│   └── imagegen.py      # Image generation logic
├── cache/               # Generated summary images
├── .env                 # Environment variables (not in git)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- **FastAPI** - Web framework
- **SQLModel** - SQL database ORM
- **PyMySQL** - MySQL database driver
- **httpx** - HTTP client for external APIs
- **Pillow** - Image generation
- **python-dotenv** - Environment variable management
- **uvicorn** - ASGI server

## Troubleshooting

### Database Connection Error

Ensure MySQL is running and credentials in `.env` are correct:

```bash
mysql -u root -p
```

### External API Timeout

The API has a 10-second timeout. If external APIs are slow, adjust `REQUEST_TIMEOUT` in `.env`.

### Missing Summary Image

Run `/countries/refresh` at least once to generate the summary image.

### Port Already in Use

Change the port in `.env` or when running uvicorn:

```bash
uvicorn app.main:app --port 8001
```

## License

This project is part of the HNG Internship program.

## Resources

- [HNG Internship](https://hng.tech/internship)
- [Hire Python Developers](https://hng.tech/hire/python-developers)
