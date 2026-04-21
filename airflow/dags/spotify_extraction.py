from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import sys
sys.path.insert(0, "/opt/airflow")

from extraction.auth import get_access_token
from extraction.playlists import fetch_top_tracks
from extraction.audio_features import fetch_audio_features
from extraction.artists import fetch_artists
from extraction.loader import load_top_tracks, load_audio_features, load_artists

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def task_extract_playlists(**context):
    token = get_access_token()
    tracks = fetch_top_tracks(token)
    context["ti"].xcom_push(key="tracks", value=tracks)


def task_extract_audio_features(**context):
    token = get_access_token()
    tracks = context["ti"].xcom_pull(key="tracks", task_ids="extract_playlists")
    track_ids = list({t["track_id"] for t in tracks})
    features = fetch_audio_features(token, track_ids)
    context["ti"].xcom_push(key="audio_features", value=features)


def task_extract_artists(**context):
    token = get_access_token()
    tracks = context["ti"].xcom_pull(key="tracks", task_ids="extract_playlists")
    artist_ids = list({t["artist_id"] for t in tracks if t["artist_id"]})
    artists = fetch_artists(token, artist_ids)
    context["ti"].xcom_push(key="artists", value=artists)


def task_load_bronze(**context):
    ti = context["ti"]
    tracks = ti.xcom_pull(key="tracks", task_ids="extract_playlists")
    features = ti.xcom_pull(key="audio_features", task_ids="extract_audio_features")
    artists = ti.xcom_pull(key="artists", task_ids="extract_artists")

    load_top_tracks(tracks)
    load_audio_features(features)
    load_artists(artists)


with DAG(
    dag_id="spotify_extraction",
    default_args=default_args,
    description="Extrai dados do Spotify e carrega na camada Bronze (DuckDB)",
    schedule_interval="@weekly",
    start_date=datetime(2026, 4, 21),
    catchup=False,
    tags=["spotify", "bronze", "extraction"],
) as dag:

    extract_playlists = PythonOperator(
        task_id="extract_playlists",
        python_callable=task_extract_playlists,
    )

    extract_audio_features = PythonOperator(
        task_id="extract_audio_features",
        python_callable=task_extract_audio_features,
    )

    extract_artists = PythonOperator(
        task_id="extract_artists",
        python_callable=task_extract_artists,
    )

    load_bronze = PythonOperator(
        task_id="load_bronze",
        python_callable=task_load_bronze,
    )

    trigger_transformation = TriggerDagRunOperator(
        task_id="trigger_transformation",
        trigger_dag_id="spotify_transformation",
        wait_for_completion=False,
    )

    extract_playlists >> [extract_audio_features, extract_artists] >> load_bronze >> trigger_transformation
