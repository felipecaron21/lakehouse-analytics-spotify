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
            country       VARCHAR,
            loaded_at     DATE
        )
    """)
    loaded_at = date.today().isoformat()
    rows = [(
        r["track_id"], r["track_name"], r["popularity"],
        r["artist_id"], r["artist_name"], r["album_name"],
        r["position"], r["country"], loaded_at,
    ) for r in records]
    conn.executemany(
        "INSERT INTO bronze.raw_top_tracks VALUES (?,?,?,?,?,?,?,?,?)", rows
    )
    conn.close()


def load_audio_features(records: list[dict]) -> None:
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bronze.raw_audio_features (
            track_id          VARCHAR,
            danceability      DOUBLE,
            energy            DOUBLE,
            valence           DOUBLE,
            tempo             DOUBLE,
            loudness          DOUBLE,
            acousticness      DOUBLE,
            instrumentalness  DOUBLE,
            speechiness       DOUBLE,
            loaded_at         DATE
        )
    """)
    loaded_at = date.today().isoformat()
    rows = [(
        r["track_id"], r["danceability"], r["energy"], r["valence"],
        r["tempo"], r["loudness"], r["acousticness"],
        r["instrumentalness"], r["speechiness"], loaded_at,
    ) for r in records]
    conn.executemany(
        "INSERT INTO bronze.raw_audio_features VALUES (?,?,?,?,?,?,?,?,?,?)", rows
    )
    conn.close()


def load_artists(records: list[dict]) -> None:
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bronze.raw_artists (
            artist_id    VARCHAR,
            artist_name  VARCHAR,
            genres       VARCHAR,
            popularity   INTEGER,
            followers    BIGINT,
            loaded_at    DATE
        )
    """)
    loaded_at = date.today().isoformat()
    rows = [(
        r["artist_id"], r["artist_name"],
        json.dumps(r["genres"]),
        r["popularity"], r["followers"], loaded_at,
    ) for r in records]
    conn.executemany(
        "INSERT INTO bronze.raw_artists VALUES (?,?,?,?,?,?)", rows
    )
    conn.close()
