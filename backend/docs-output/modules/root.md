# root

**Purpose:** To provide a quick, isolated test environment for database connectivity. It helps engineers pinpoint whether database connection problems (e.g., slowness, timeouts, hangs) are occurring at the fundamental driver level or within the connection pooling mechanism, by testing each component separately and reporting timings.

**Description:** A standalone diagnostic script designed to identify and isolate issues with database connections, specifically targeting potential hangs or slowness in either the bare `psycopg` driver or the `psycopg_pool` connection management layer.

## Key Files

- `diagnose_db.py`

## Dependencies

- time
- psycopg
- psycopg_pool
