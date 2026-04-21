from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import sys
sys.path.insert(0, "/opt/airflow")

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

DBT_DIR = "/opt/airflow/dbt"
DBT_CMD = f"cd {DBT_DIR} && dbt"


def task_export_to_postgres():
    from export.duckdb_to_postgres import export
    export()


with DAG(
    dag_id="spotify_transformation",
    default_args=default_args,
    description="Executa modelos dbt (Silver e Gold) e exporta para PostgreSQL",
    schedule_interval=None,  # disparado pelo DAG de extração
    start_date=datetime(2026, 4, 21),
    catchup=False,
    tags=["spotify", "silver", "gold", "dbt"],
) as dag:

    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=f"{DBT_CMD} run --select silver --profiles-dir {DBT_DIR}",
    )

    dbt_test_silver = BashOperator(
        task_id="dbt_test_silver",
        bash_command=f"{DBT_CMD} test --select silver --profiles-dir {DBT_DIR}",
    )

    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=f"{DBT_CMD} run --select gold --profiles-dir {DBT_DIR}",
    )

    dbt_test_gold = BashOperator(
        task_id="dbt_test_gold",
        bash_command=f"{DBT_CMD} test --select gold --profiles-dir {DBT_DIR}",
    )

    export_to_postgres = PythonOperator(
        task_id="export_to_postgres",
        python_callable=task_export_to_postgres,
    )

    dbt_run_silver >> dbt_test_silver >> dbt_run_gold >> dbt_test_gold >> export_to_postgres
