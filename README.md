# Corteva Weather Data API

A Django REST API that ingests historical weather data from 167 Midwest weather stations, computes yearly statistics, and serves everything through a clean, paginated REST API with Swagger documentation.

The full dataset covers 30 years of data (1985–2014), totaling 1.7 million records across Nebraska, Iowa, Illinois, Indiana, and Ohio — all under 45MB.

---

## What it does

- **Data Ingestion** — reads raw `.txt` weather files and loads them into PostgreSQL, with built-in deduplication so running it twice won't create duplicate records
- **Statistics Calculation** — computes average max/min temperatures and total precipitation per station per year, stored separately for fast querying
- **REST API** — paginated endpoints for weather observations and statistics, filterable by station and date
- **Swagger UI** — auto-generated interactive API documentation for easy testing

---

## Core Requirements

- Python 3.10+
- PostgreSQL
- Docker (optional, but recommended)

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd corteva-assessment-kc/src
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up your environment variables

Create a `.env` file inside `src/`:

```env
DATABASE_URL=your-database-connection-url
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 4. Start PostgreSQL

If you don't have PostgreSQL installed locally, spin it up with Docker:

```bash
docker run --name [container-name] \
  -e POSTGRES_DB=[database-name] \
  -e POSTGRES_USER=[username] \
  -e POSTGRES_PASSWORD=[password] \
  -p 5432:5432 \
  -d postgres:15
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Ingest the weather data

```bash
python ingestion/ingest.py wx_data
```

This reads all station files from the `wx_data/` directory, converts raw values to standard units, and loads them into the database. Running it more than once is safe — duplicates are automatically skipped.

### 7. Calculate statistics

```bash
python ingestion/analyze.py
```

This computes average temperatures and total precipitation for every station and year, and stores the results in the `weather_stats` table.

### 8. Start the API server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

---

## Running with Docker Compose

If you'd rather skip the setup steps above, Docker Compose handles everything in one command:

```bash
docker-compose up db
```

This starts both PostgreSQL and the Django API together. The API will be live at `http://localhost:8000` and ready to use.

---

## API Endpoints

### GET `/api/weather/`

Returns paginated weather observations. You can filter by station ID and/or date.

| Parameter | Type | Description |
|---|---|---|
| `station_id` | string | e.g. `USC00110072` |
| `date` | string | e.g. `1985-01-01` |
| `page` | integer | page number |

```
GET /api/weather/?station_id=USC00110072&date=1985-01-01
```

### GET `/api/weather/stats/`

Returns paginated yearly statistics per station.

| Parameter | Type | Description |
|---|---|---|
| `station_id` | string | e.g. `USC00110072` |
| `year` | integer | e.g. `1985` |
| `page` | integer | page number |

```
GET /api/weather/stats/?station_id=USC00110072&year=1985
```

### API Documentation

| URL | What it is |
|---|---|
| `/api/swagger/` | Interactive Swagger UI — try the endpoints directly in the browser |
| `/api/redoc/` | ReDoc documentation |
| `/api/schema/` | Raw OpenAPI schema in YAML |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Data Modeling

The schema is split into three tables. See [data_modeling](answers/database_schema.txt) for the full breakdown.

---

## Ingestion Performance

The ingestion script was benchmarked on the full 1.7M row dataset across several approaches:

| Approach | Duration |
|---|---|
| Per-file transactions (baseline) | 130s |
| `bulk_create` with batch_size=1000 | 110s |
| `bulk_create` with batch_size=5000 | 105s |
| Raw psycopg2 `COPY` | 70s |

The final implementation uses Django ORM `bulk_create` with `ignore_conflicts=True`. This keeps the code readable and maintainable while still being fast enough for the use case. In production, daily incremental runs process around 167 new records and complete in under a second.

---

## AWS Deployment

See [aws_deployment](answers/aws_deployment.txt) for the full writeup.

The proposed architecture uses Lambda + API Gateway + RDS, which is the most cost-effective setup for a dataset of this size:

```
S3 (raw wx_data files)
        ↓
EventBridge (nightly cron)
        ↓
Lambda (runs ingest.py + analyze.py)
        ↓
RDS PostgreSQL
        ↑
API Gateway → Lambda (Django API via Mangum)
```

Since the entire 30-year historical dataset is under 45MB, there's no need for always-on compute. The estimated monthly cost is around **$20**, with RDS being the largest expense.

---

## Extra Features Worth Noting

- **Django Admin** — available at `/admin/` for browsing and managing data directly in the browser
- **OpenAPI schema** — both Swagger UI and ReDoc are available out of the box
- **Idempotent scripts** — both `ingest.py` and `analyze.py` can be run repeatedly without side effects