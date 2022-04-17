from datetime import timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "Jordan",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "start_date": datetime(2021, 8, 14),
}


with DAG(
    dag_id="first_dag",
    description="This is our first dag we write",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
) as dag:

    t1 = BashOperator(
        task_id="first_task", bash_command="echo hello world, this is our first task!"
    )

    t2 = BashOperator(
        task_id="second_task",
        bash_command="echo hey, I am task2 I will running after task 1",
    )

    t3 = BashOperator(
        task_id="third_task",
        bash_command="echo hey, I am task 3 and will be running at the same time as task 2",
    )

    t1 >> [t2, t3]
