"""DAG d'orchestration du pipeline Big Data : generate -> ingest (Spark) -> load (Postgres)."""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-eng",
    "retries": 1,
}

with DAG(
    dag_id="big_data_pipeline",
    description="Génération, ingestion Spark et chargement Postgres des commandes e-commerce",
    default_args=default_args,
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["spark", "postgres", "big-data"],
) as dag:

    generate = BashOperator(
        task_id="generate_data",
        bash_command="python /opt/scripts/generate_data.py",
    )

    ingest = BashOperator(
        task_id="ingest_spark",
        bash_command="python /opt/scripts/ingest_spark.py",
    )

    load = BashOperator(
        task_id="load_to_postgres",
        bash_command="python /opt/scripts/load_to_postgres.py",
        env={
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "bigdata",
            "POSTGRES_USER": "bigdata",
            "POSTGRES_PASSWORD": "bigdata",
        },
    )

    generate >> ingest >> load
