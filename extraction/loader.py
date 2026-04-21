import json
from datetime import date

import duckdb


DB_PATH = "/opt/airflow/data/spotify.duckdb"


def _connect() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(DB_PATH)
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze")
    return conn


def load_top_tracks(records: list[dict]) -> None:
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bronze.raw_top_tracks (
            track_id      VARCHAR,
            track_name    VARCHAR,
            popularity    INTEGER,
            artist_id     VARCHAR,
            artist_name   VARCHAR,
            album_name    VARCHAR,
            position      INTEGER,
            time_range    VARCHAR,
            loaded_at     DATE
        )
    """)
    loaded_at = date.today().isoformat()
    rows = [(
        r["track_id"], r["track_name"], r["popularity"],
        r["artist_id"], r["artist_name"], r["album_name"],
        r["position"], r["time_range"], loaded_at,
    ) for r in records]
    conn.executemany(
        "INSERT INTO bronze.raw_top_tracks VALUES (?,?,?,?,?,?,?,?,?)", rows
    )
    conn.close()


def load_top_artists(records: list[dict]) -> None:
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bronze.raw_top_artists (
            artist_id    VARCHAR,
            artist_name  VARCHAR,
            genres       VARCHAR,
            popularity   INTEGER,
            followers    BIGINT,
            position     INTEGER,
            time_range   VARCHAR,
            loaded_at    DATE
        )
    """)
    loaded_at = date.today().isoformat()
    rows = [(
        r["artist_id"], r["artist_name"],
        json.dumps(r["genres"]),
        r["popularity"], r["followers"],
        r["position"], r["time_range"], loaded_at,
    ) for r in records]
    conn.executemany(
        "INSERT INTO bronze.raw_top_artists VALUES (?,?,?,?,?,?,?,?)", rows
    )
    conn.close()


def load_recently_played(records: list[dict]) -> None:
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bronze.raw_recently_played (
            track_id     VARCHAR,
            track_name   VARCHAR,
            artist_id    VARCHAR,
            artist_name  VARCHAR,
            album_name   VARCHAR,
            played_at    VARCHAR,
            loaded_at    DATE
        )
    """)
    loaded_at = date.today().isoformat()
    rows = [(
        r["track_id"], r["track_name"],
        r["artist_id"], r["artist_name"],
        r["album_name"], r["played_at"], loaded_at,
    ) for r in records]
    conn.executemany(
        "INSERT INTO bronze.raw_recently_played VALUES (?,?,?,?,?,?,?)", rows
    )
    conn.close()
