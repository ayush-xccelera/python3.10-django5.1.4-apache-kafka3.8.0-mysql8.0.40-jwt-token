# Product Inventory API

Django + Django REST Framework backend for authenticated product & inventory
management, backed by MySQL, JWT auth, and Kafka domain events.

## Stack

- Python 3.10.16 (target) / Django 5.1.4
- Django REST Framework
- MySQL 8.0.40 (via PyMySQL driver, no compiled dependency required)
- djangorestframework-simplejwt (JWT auth, HS256, 30 min access token, no refresh rotation)
- kafka-python (publishes `STOCK_UPDATED` events)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py seed   # optional demo data (idempotent)
```

## Run

```bash
chmod +x start.sh
PORT=20550 ./start.sh
```

Server listens on `http://localhost:20550/`.

## Environment variables (`.env_31ba26a6-f289-40e8-818c-95589081c8c8`)

| Variable | Purpose |
|---|---|
| SECRET_KEY | Django secret key |
| DEBUG | Debug flag |
| DB_ENGINE / DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT | MySQL connection |
| KAFKA_BOOTSTRAP_SERVERS | Kafka broker address (default `localhost:9092`) |
| KAFKA_STOCK_UPDATED_TOPIC | Topic name for stock events (default `stock-updated`) |
| PORT | HTTP port (default 20550) |

## Auth

- `POST /api/v1/auth/register` — create a user (username, email, password). Not part
  of the original spec but required as the direct, unavoidable consequence of needing
  accounts to log in with.
- `POST /api/v1/auth/login` — authenticate, returns `access` (JWT, 30 min) and `refresh`.
- `GET /api/v1/auth/me` — return the current authenticated user.

All `/api/v1/products/*` endpoints require `Authorization: Bearer <access token>`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/v1/auth/register | Register a user |
| POST | /api/v1/auth/login | Login, get JWT |
| GET | /api/v1/auth/me | Current user |
| POST | /api/v1/products/ | Create product |
| GET | /api/v1/products/ | List active products (paginated) |
| GET | /api/v1/products/{id}/ | Retrieve product by id |
| PUT | /api/v1/products/{id}/ | Update name/description/price |
| PATCH | /api/v1/products/{id}/stock/ | Adjust stock (`delta` or `quantity`), rejects negative result |
| PATCH | /api/v1/products/{id}/deactivate/ | Set status to INACTIVE |
| PATCH | /api/v1/products/{id}/activate/ | Set status to ACTIVE |
| DELETE | /api/v1/products/{id}/ | Delete product |

Pagination: `LimitOffsetPagination`, default `limit=20`, max `limit=100`, via
`?limit=&offset=` query params. Response shape: `{count, next, previous, results}`.

## Kafka

On every successful stock change (`PATCH /products/{id}/stock/`), a `STOCK_UPDATED`
event is published to the `stock-updated` topic with:

```json
{
  "event": "STOCK_UPDATED",
  "product_id": 1,
  "previous_stock_quantity": 10,
  "new_stock_quantity": 15,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Tests

```bash
pytest -v
```

16 tests covering auth (register/login/me/invalid token) and product CRUD +
stock/activate/deactivate business rules.

## Project layout

```
config/            Django project settings, root URLconf
products/          App: models, serializers, views, urls, auth, kafka producer, seed cmd
tests/              pytest-django test suite
requirements.txt
start.sh / start.bat
.env_31ba26a6-f289-40e8-818c-95589081c8c8
```
