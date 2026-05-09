import os
import duckdb
import psycopg2
from psycopg2.extras import execute_values


DB_PATH = "/opt/airflow/data/spotify.duckdb"

GOLD_TABLES = [
    "top_tracks_by_period",
    "top_artists_by_period",
    "listening_history",
    "listening_patterns",
]


def _pg_conn():
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname="spotify_analytics",
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def _duckdb_type_to_pg(duckdb_type: str) -> str:
    mapping = {
        "VARCHAR": "TEXT",
        "DOUBLE": "DOUBLE PRECISION",
        "FLOAT": "REAL",
        "INTEGER": "INTEGER",
        "BIGINT": "BIGINT",
        "DATE": "DATE",
        "BOOLEAN": "BOOLEAN",
        "TIMESTAMP": "TIMESTAMP",
    }
    return mapping.get(duckdb_type.upper(), "TEXT")


def export():
    duck = duckdb.connect(DB_PATH)
    pg = _pg_conn()
    pg_cursor = pg.cursor()

    for table in GOLD_TABLES:
        print(f"Exporting gold.{table}...")

        df = duck.execute(f"SELECT * FROM main_gold.{table}").fetchdf()

        if df.empty:
            print(f"  Skipped — no data in gold.{table}")
            continue

        columns = list(df.columns)
        col_defs = ", ".join(f'"{c}" TEXT' for c in columns)

        pg_cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
        pg_cursor.execute(f'CREATE TABLE "{table}" ({col_defs})')

        rows = [tuple(str(v) if v is not None else None for v in row) for row in df.itertuples(index=False)]
        placeholders = "(" + ", ".join(["%s"] * len(columns)) + ")"
        col_names = ", ".join(f'"{c}"' for c in columns)

        execute_values(
            pg_cursor,
            f'INSERT INTO "{table}" ({col_names}) VALUES %s',
            rows,
        )

        pg.commit()
        print(f"  Done — {len(rows)} rows inserted.")

    duck.close()
    pg_cursor.close()
    pg.close()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    export()
