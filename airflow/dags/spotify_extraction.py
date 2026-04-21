from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import sys
sys.path.insert(0, "/opt/airflow")

from extraction.auth import get_access_token
from extraction.top_tracks import fetch_top_tracks
from extraction.top_artists import fetch_top_artists
from extraction.recently_played import fetch_recently_played
from extraction.loader import load_top_tracks, load_top_artists, load_recently_played

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def task_extract_top_tracks(**context):
    token = get_access_token()
    tracks = fetch_top_tracks(token)
    context["ti"].xcom_push(key="top_tracks", value=tracks)


def task_extract_top_artists(**context):
    token = get_access_token()
    artists = fetch_top_artists(token)
    context["ti"].xcom_push(key="top_artists", value=artists)


def task_extract_recently_played(**context):
    token = get_access_token()
    played = fetch_recently_played(token)
    context["ti"].xcom_push(key="recently_played", value=played)


def task_load_bronze(**context):
    ti = context["ti"]
    top_tracks = ti.xcom_pull(key="top_tracks", task_ids="extract_top_tracks")
    top_artists = ti.xcom_pull(key="top_artists", task_ids="extract_top_artists")
    recently_played = ti.xcom_pull(key="recently_played", task_ids="extract_recently_played")

    load_top_tracks(top_tracks)
    load_top_artists(top_artists)
    load_recently_played(recently_played)


with DAG(
    dag_id="spotify_extraction",
    default_args=default_args,
    description="Extrai dados pessoais do Spotify e carrega na camada Bronze (DuckDB)",
    schedule="@weekly",
    start_date=datetime(2026, 4, 21),
    catchup=False,
    tags=["spotify", "bronze", "extraction"],
) as dag:

    extract_top_tracks = PythonOperator(
        task_id="extract_top_tracks",
        python_callable=task_extract_top_tracks,
    )

    extract_top_artists = PythonOperator(
        task_id="extract_top_artists",
        python_callable=task_extract_top_artists,
    )

    extract_recently_played = PythonOperator(
        task_id="extract_recently_played",
        python_callable=task_extract_recently_played,
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

    [extract_top_tracks, extract_top_artists, extract_recently_played] >> load_bronze >> trigger_transformation
