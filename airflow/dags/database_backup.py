import os
import tempfile
from datetime import datetime

import fastavro
import pandas as pd
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models.param import Param
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from airflow import DAG
from utils.db import get_avro_schema

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
}

dag = DAG(
    "db_table_to_avro",
    default_args=default_args,
    description="A simple DAG to backup a database table to a blob storage in Avro format",
    schedule_interval=None,
    params={
        "db_connection_id": Param(type="string", default="data_db"),
        "blob_storage_connection_id": Param(type="string", default="minio"),
        "table_name": Param(type="string", default="user"),
        "output_bucket": Param(type="string", default="prd-data"),
        "output_location": Param(type="string", default="backups"),
        "output_filename": Param(type="string", default="user.avro"),
    },
)


def backup_database_table(**kwargs):
    # Get Database Connection
    db_hook = PostgresHook.get_hook(kwargs["params"]["db_connection_id"])
    conn = db_hook.get_conn()
    engine = db_hook.get_sqlalchemy_engine()

    # Get Avro schema
    table_name = kwargs["params"]["table_name"]
    avro_schema = get_avro_schema(engine, table_name)

    # Query the Database
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)

    # Create a temporary file to store the Avro data
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    fastavro.writer(temp_file, avro_schema, df.to_dict("records"))
    temp_file.close()

    return temp_file.name


def upload_to_blob_storage(**kwargs):
    hook = S3Hook(aws_conn_id=kwargs["params"]["blob_storage_connection_id"])

    task_instance = kwargs["task_instance"]
    temp_file_name = task_instance.xcom_pull(task_ids="backup_database_table")

    output_bucket = kwargs["params"]["output_bucket"]
    output_location = kwargs["params"]["output_location"]
    output_filename = kwargs["params"]["output_filename"]

    # Create the key for the object
    key = f"{output_location}/{output_filename}"

    hook.load_file(
        filename=temp_file_name,
        key=key,
        bucket_name=output_bucket,
        replace=True,
    )


def remove_temp_file(**kwargs):
    # Get the temporary file name from the previous task
    task_instance = kwargs["task_instance"]
    temp_file_name = task_instance.xcom_pull(task_ids="backup_database_table")

    if os.path.exists(temp_file_name):
        os.remove(temp_file_name)


remove_temp_file_task = PythonOperator(
    task_id="remove_temp_file",
    python_callable=remove_temp_file,
    provide_context=True,
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag,
)


backup_task = PythonOperator(
    task_id="backup_database_table",
    python_callable=backup_database_table,
    provide_context=True,
    dag=dag,
)

upload_task = PythonOperator(
    task_id="upload_to_blob_storage",
    python_callable=upload_to_blob_storage,
    provide_context=True,
    dag=dag,
)

backup_task >> upload_task >> remove_temp_file_task
