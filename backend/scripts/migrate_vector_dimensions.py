"""One-off migration: resize embeddings.vector to match the current
embedder's dimensionality (e.g. after switching from Gemini's 768-dim
vectors to the local sentence-transformers model's 384-dim vectors).

Run once from backend/:
    python scripts/migrate_vector_dimensions.py 384

Truncates the embeddings table first — pgvector can't resize a column
in place while it holds vectors of a different dimension, and any
existing rows are from a previous provider anyway, so they need to be
re-embedded and re-stored regardless.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/migrate_vector_dimensions.py <new_dimensions>")

    new_dims = int(sys.argv[1])

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        sys.exit("DATABASE_URL is not set.")

    import psycopg

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM embeddings")
            (existing_rows,) = cur.fetchone()
            print(f"embeddings table currently has {existing_rows} row(s)")

            print("Truncating embeddings table...")
            cur.execute("TRUNCATE TABLE embeddings")

            print(f"Resizing vector column to vector({new_dims})...")
            cur.execute(f"ALTER TABLE embeddings ALTER COLUMN vector TYPE vector({new_dims})")

        conn.commit()

    print(f"Done. embeddings.vector is now vector({new_dims}). Re-run the pipeline to repopulate it.")


if __name__ == "__main__":
    main()