FROM apache/airflow:2.8.4-python3.11

USER airflow
RUN pip install --no-cache-dir \
    duckdb==0.10.2 \
    dbt-core==1.7.10 \
    dbt-duckdb==1.7.3 \
    requests==2.31.0 \
    python-dotenv==1.0.1 \
    psycopg2-binary==2.9.9
