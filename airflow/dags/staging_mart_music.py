from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime


default_args = {
    "depends_on_past": False,
    "email": ["kojordan9112@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "start_date": datetime(2020, 1, 1),
}

with DAG(
    dag_id="start_music_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # task 1
    warmup_task = DummyOperator(task_id="warmup_task")

    bash_cmd = "dbt run --project-dir /home/airflow/gcs/dags --profiles-dir /home/airflow/gcs/data/profiles"

    bash_task = BashOperator(task_id="dbt_task", bash_command=bash_cmd)

    warmup_task >> bash_task
