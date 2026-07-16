# root

**Purpose:** To provide a quick and isolated way to troubleshoot database connection problems, helping engineers determine if a slow or stuck connection originates from the underlying database driver (psycopg) or the connection pooling mechanism (psycopg_pool). It is intended to be run directly, not imported as a library.

**Description:** A standalone diagnostic script for testing PostgreSQL database connectivity and identifying potential bottlenecks or issues at different layers (bare connection vs. connection pool).

## Key Files

- `diagnose_db.py`

## Dependencies

- time
- psycopg
- psycopg_pool
