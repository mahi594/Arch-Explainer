"""Run this directly to isolate a hanging DB connection:

    python diagnose_db.py

Tests each layer separately so we know exactly which one is slow/stuck.
"""
import time

DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5433/arch_explainer"

print("1. Bare psycopg connection (no pool)...")
start = time.time()
import psycopg
conn = psycopg.connect(DATABASE_URL, connect_timeout=5)
print(f"   OK in {time.time() - start:.2f}s")
conn.execute("SELECT 1")
print("   SELECT 1 worked")
conn.close()

print("2. ConnectionPool, opened explicitly...")
start = time.time()
from psycopg_pool import ConnectionPool
pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=5, open=False)
pool.open(wait=True, timeout=10)
print(f"   OK in {time.time() - start:.2f}s")
with pool.connection() as conn:
    conn.execute("SELECT 1")
print("   pool SELECT 1 worked")
pool.close()

print("\nAll good — the connection layer itself isn't the problem.")