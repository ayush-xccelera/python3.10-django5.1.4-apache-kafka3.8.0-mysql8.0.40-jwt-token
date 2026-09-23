COMMIT_MESSAGE: Add StockHistory tracking and GET /products/{id}/stock-history endpoint

## Summary
Asked to track every stock quantity change on a Product as a StockHistory row,
and expose that history through a new authenticated, paginated endpoint. I added
a StockHistory model tied to Product, wired it into the existing stock-update
action so it only fires on a successful change, and added a new JWT-protected
GET endpoint that returns the history newest-first with 404 handling for
missing products.

## Features Added
- New `StockHistory` model (id, product FK, previous_quantity, new_quantity, changed_at auto_now_add) ordered newest-first.
- `PATCH /api/v1/products/{id}/stock/` now creates exactly one `StockHistory` row on every successful stock change (before publishing the existing STOCK_UPDATED Kafka event). Rejected changes (e.g. negative resulting stock) create no history row.
- No history row is created for product creation, deactivation, reactivation, or name/description/price updates.
- New `GET /api/v1/products/{id}/stock-history/` endpoint:
  - Requires JWT authentication (401 if missing/invalid token).
  - Returns 404 if the product does not exist.
  - Returns paginated stock-change history (newest first), using the same `DefaultLimitOffsetPagination` (limit/offset, default 20) as `GET /api/v1/products/`.

## Files Modified
- `products/models.py` — added `StockHistory` model.
- `products/serializers.py` — added `StockHistorySerializer`.
- `products/views.py` — `stock` action now creates a `StockHistory` row on success; added `stock_history` action (`GET .../stock-history/`) using `get_object_or_404` + `DefaultLimitOffsetPagination`.
- `products/admin.py` — registered `Product` and `StockHistory` in admin.
- `config/settings.py` — env file path corrected to `.env_146e1472411e7cf2`; `DATABASES` OPTIONS made conditional so the `charset` option (MySQL-only) isn't passed to a Postgres backend.
- `tests/test_products.py` — added tests covering history creation on success, no history on rejection/other updates, 401/404 on the history endpoint, and newest-first pagination.

## Files Added
- `products/migrations/0003_stockhistory.py` — migration creating the `StockHistory` table.
- `.env_146e1472411e7cf2` — environment file with DB and Kafka settings for this session.

## Secrets Extracted
- None hardcoded were found beyond existing `SECRET_KEY` default already using `os.getenv`; SECRET_KEY value also mirrored into `.env_146e1472411e7cf2` for local runs.

## DB URLs Resolved
- No DB URL existed in the repo previously (defaults pointed at a MySQL instance not available in this sandbox). Called `create_db()` to provision a fresh local Postgres database: `postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_ff572eb7c6d7`. Configured via `DB_ENGINE=django.db.backends.postgresql` and related `DB_*` vars in `.env_146e1472411e7cf2`.

## Test Results Summary
22 PASSED, 0 FAILED, 0 SKIPPED (pytest suite, includes 6 new stock-history tests). Manual curl verification of register/login/create product/stock update (success + rejection)/deactivate/activate/stock-history (200, 401, 404) also all passed.
