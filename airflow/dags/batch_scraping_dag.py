from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess, sys, os

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def run_avito():
    sys.path.insert(0, "/opt/scrapers")
    from avito_scraper import scrape_avito
    from scraper_utils import save_to_bronze
    data = scrape_avito(max_pages=3)
    save_to_bronze(data, "avito")
    return len(data)

def run_wandaloo():
    sys.path.insert(0, "/opt/scrapers")
    from wandaloo_scraper import scrape_wandaloo
    from scraper_utils import save_to_bronze
    data = scrape_wandaloo(max_pages=2)
    save_to_bronze(data, "wandaloo")
    return len(data)

with DAG(
    dag_id="batch_scraping_auto",
    default_args=default_args,
    description="Scraping toutes les heures des annonces automobiles",
    schedule_interval="0 * * * *",  # Toutes les heures
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["scraping", "automobile"],
) as dag:

    task_avito = PythonOperator(
        task_id="scrape_avito",
        python_callable=run_avito,
    )

    task_wandaloo = PythonOperator(
        task_id="scrape_wandaloo",
        python_callable=run_wandaloo,
    )

    task_avito >> task_wandaloo