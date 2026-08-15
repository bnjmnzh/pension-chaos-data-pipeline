from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pension_members_elt_pipeline",
    default_args=default_args,
    description="Orchestrates Bronze raw ingestion, freshness checks, dbt transformations, and data tests.",
    schedule_interval="0 6 * * *",  # Daily 06:00
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["pension", "dbt", "bronze", "silver"],
) as dag:
    # 1. Ingestion: Execute Python script to ingest raw payloads into Bronze (raw.members)
    run_ingestion = BashOperator(
        task_id="run_ingestion_script",
        bash_command="python /opt/airflow/dags/scripts/ingest.py",
    )

    # 2. Source Freshness: Ensure Bronze data arrived on SLA before running dbt
    check_source_freshness = BashOperator(
        task_id="check_source_freshness",
        bash_command="cd /opt/airflow/dbt_project && dbt source freshness",
    )

    # 3. Model Building: Transform raw JSON into Silver stg_members view/table
    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="cd /opt/airflow/dbt_project && dbt run --select staging",
    )

    # 4. Data Quality Gate: Run schema & invariant tests on Silver tables
    test_dbt_models = BashOperator(
        task_id="test_dbt_models",
        bash_command="cd /opt/airflow/dbt_project && dbt test --select staging",
    )

    # Pipeline Order: Ingest -> Freshness -> dbt Run -> dbt Test
    run_ingestion >> check_source_freshness >> run_dbt_models >> test_dbt_models