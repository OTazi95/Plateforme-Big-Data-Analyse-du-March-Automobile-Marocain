from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Ajouter le chemin des scripts au PYTHONPATH
sys.path.insert(0, '/opt/airflow/dags/scripts')

# Importer les fonctions des scripts
from bronze_to_silver import transform_bronze_to_silver
from silver_to_gold import load_silver, build_gold_tables
from great_expectations_checks import run_quality_checks

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def silver_pipeline():
    """Exécute la transformation Silver (lecture Bronze -> nettoyage -> écriture Silver)"""
    transform_bronze_to_silver()

def gold_pipeline():
    """Exécute la transformation Gold (lecture Silver -> chargement PostgreSQL)"""
    df = load_silver()
    if not df.empty:
        build_gold_tables(df)
        print(f"{len(df)} lignes chargées dans les tables Gold")
    else:
        print("Aucune donnée Silver trouvée")

with DAG(
    dag_id="medallion_pipeline",
    default_args=default_args,
    description="Pipeline Bronze → Silver → Gold",
    schedule_interval="30 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["medallion", "etl"],
) as dag:

    bronze_to_silver = PythonOperator(
        task_id="bronze_to_silver",
        python_callable=silver_pipeline,
    )

    quality_checks = PythonOperator(
        task_id="quality_checks",
        python_callable=run_quality_checks,
    )

    silver_to_gold = PythonOperator(
        task_id="silver_to_gold",
        python_callable=gold_pipeline,
    )

    bronze_to_silver >> quality_checks >> silver_to_gold