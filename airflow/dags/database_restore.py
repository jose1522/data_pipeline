import os
import tempfile
from datetime import datetime

import fastavro
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import Variable
from airflow.models.param import Param
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from loguru import logger

from airflow import DAG

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"/tmp/restore_database_{current_time}.log"
logger.add(log_filename)

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
}

dag = DAG(
    "restore_db_from_avro",
    default_args=default_args,
    description="A simple DAG to backup a database table to a blob storage in Avro format",
    schedule_interval=None,
    params={
        "db_connection_id": Param(type="string", default="data_db"),
        "blob_storage_connection_id": Param(type="string", default="minio"),
        "table_name": Param(type="string", default="user"),
        "input_bucket": Param(type="string", default="prd-data"),
        "input_location": Param(type="string", default="backups"),
        "input_filename": Param(type="string", default="user.avro"),
        "file_version": Param(type="string", default="v1"),
    },
)


def fetch_from_blob_storage(**kwargs):
    db_hook = PostgresHook(kwargs["params"]["db_connection_id"])
    hook = S3Hook(aws_conn_id=kwargs["params"]["blob_storage_connection_id"])

    output_bucket = kwargs["params"]["input_bucket"]
    output_location = kwargs["params"]["input_location"]
    output_filename = kwargs["params"]["input_filename"]
    table_name = kwargs["params"]["table_name"]

    # Create the key for the object
    key = f"{output_location}/{output_filename}"

    # Create a temporary file to save the fetched Avro data
    temp_dir = tempfile.TemporaryDirectory()

    temp_file_name = hook.download_file(
        key=key, bucket_name=output_bucket, local_path=temp_dir.name
    )

    # Read Avro data
    with open(temp_file_name, "rb") as f:
        reader = fastavro.reader(f)
        records = [r for r in reader]

    # Insert into database

    try:
        conn = db_hook.get_conn()
        cursor = conn.cursor()

        # Delete existing data from table
        cursor.execute(f"DELETE FROM {table_name}")
        logger.info(f"Deleted all records from {table_name}")

        # Insert new data
        for record in records:
            placeholders = ", ".join(["%s"] * len(record))
            columns = ", ".join(record.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(record.values()))

        conn.commit()

    except Exception as e:
        logger.error(f"Error inserting into {table_name}: {e}")
        conn.rollback()


def upload_log_to_s3(**kwargs):
    s3_hook = S3Hook(kwargs["params"]["blob_storage_connection_id"])
    log_filename = kwargs["log_filename"]
    output_bucket = Variable.get("log_bucket")

    *_, name = os.path.split(log_filename)
    key = f"dags/{name}"

    print(f"Uploading log file to {output_bucket}/{key}")

    try:
        s3_hook.load_file(
            filename=log_filename, key=key, bucket_name=output_bucket, replace=True
        )
        logger.info(f"Successfully uploaded log file to {key}")
    except Exception as e:
        logger.error(f"Failed to upload log file: {e}")
    finally:
        if os.path.exists(log_filename):
            os.remove(log_filename)


restore_from_backup = PythonOperator(
    task_id="restore_from_backup",
    python_callable=fetch_from_blob_storage,
    provide_context=True,
    dag=dag,
)


upload_log_to_s3_task = PythonOperator(
    task_id="upload_log",
    python_callable=upload_log_to_s3,
    provide_context=True,
    trigger_rule=TriggerRule.ALL_DONE,
    op_kwargs={"log_filename": log_filename},
    dag=dag,
)

restore_from_backup >> upload_log_to_s3_task
