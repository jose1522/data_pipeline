import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict

import pandas as pd
import requests
from airflow.decorators import task
from airflow.hooks.S3_hook import S3Hook
from airflow.models import Variable
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule
from loguru import logger

from airflow import DAG

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"/tmp/bulk_insert_{current_time}.log"
logger.add(log_filename)

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
}


def split_data(file_path: str, chunk_size: int = 1000) -> List[Tuple[int, int]]:
    data = pd.read_csv(file_path)
    num_rows = len(data)
    chunks = [(i, i + chunk_size) for i in range(0, num_rows, chunk_size)]
    return chunks


def process_chunk(
    file_path: str,
    offset_limit: Tuple[int, int],
    endpoint_url: str,
    use_headers: bool = True,
    column_name_map: Optional[Dict[str, str]] = None,
):
    offset, limit = offset_limit
    chunk_data = pd.read_csv(
        file_path,
        skiprows=range(0, offset),
        nrows=limit - offset,
        header="infer" if use_headers else None,
    )
    print(chunk_data)
    if column_name_map:
        new_column_name_map = {}
        for key, value in column_name_map.items():
            if key.isalnum():
                new_column_name_map[int(key)] = value
        # remove any column that is not in the map
        chunk_data = chunk_data[new_column_name_map.keys()]
        # rename the columns
        chunk_data = chunk_data.rename(columns=new_column_name_map)

    print(chunk_data)

    response = requests.post(endpoint_url, json=chunk_data.to_dict(orient="records"))
    if response.status_code > 200:
        logger.error(f"Failed to upload chunk {offset}-{limit}: {response.text}")
        response.raise_for_status()
    return response.status_code


dag = DAG(
    "bulk_data_insert",
    default_args=default_args,
    description="A simple DAG to insert data from a CSV file to a database table",
    schedule_interval=None,
    params={
        "db_connection_id": Param(type="string", default="data_db"),
        "blob_storage_connection_id": Param(type="string", default="minio"),
        "input_bucket": Param(type="string", default="prd-data"),
        "input_location": Param(type="string", default="raw"),
        "input_filename": Param(type="string", default="departments.csv"),
        "data_api_url": Param(
            type="string", default="http://data_api:8000/v1/department/bulk"
        ),
        "chunk_size": Param(type="integer", default=100),
        "use_csv_headers": Param(type="boolean", default=True),
        "column_name_map": Param(type="object", default={}),
    },
)


@task(dag=dag)
def fetch_from_blob_storage(**kwargs):
    hook = S3Hook(aws_conn_id=kwargs["params"]["blob_storage_connection_id"])

    output_bucket = kwargs["params"]["input_bucket"]
    output_location = kwargs["params"]["input_location"]
    output_filename = kwargs["params"]["input_filename"]

    # Create the key for the object
    key = f"{output_location}/{output_filename}"

    temp_file_name = hook.download_file(
        key=key, bucket_name=output_bucket, local_path="/tmp"
    )
    return temp_file_name


@task(dag=dag)
def split_task(**kwargs):
    task_instance = kwargs["task_instance"]
    file_path = task_instance.xcom_pull(task_ids="fetch_from_blob_storage")
    chunk_size = kwargs["params"]["chunk_size"]
    return split_data(file_path, chunk_size)


@task(dag=dag)
def process_chunk_task(offset_limit: Tuple[int, int], **kwargs):
    task_instance = kwargs["task_instance"]
    file_path = task_instance.xcom_pull(task_ids="fetch_from_blob_storage")
    url = kwargs["params"]["data_api_url"]
    use_headers = kwargs["params"]["use_csv_headers"]
    column_name_map = kwargs["params"]["column_name_map"]
    process_chunk(
        file_path=file_path,
        offset_limit=offset_limit,
        endpoint_url=url,
        use_headers=use_headers,
        column_name_map=column_name_map,
    )


@task(dag=dag, trigger_rule=TriggerRule.ALL_DONE)
def upload_log_to_s3(log_filename: str, **kwargs):
    s3_hook = S3Hook(kwargs["params"]["blob_storage_connection_id"])
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


@task(dag=dag, trigger_rule=TriggerRule.ALL_DONE)
def remove_temp_file(**kwargs):
    task_instance = kwargs["task_instance"]
    temp_file_name = task_instance.xcom_pull(task_ids="fetch_from_blob_storage")
    print(temp_file_name)
    if os.path.exists(temp_file_name):
        os.remove(temp_file_name)


fetch_task = fetch_from_blob_storage()
split_data_task = split_task()
parallel_tasks = process_chunk_task.expand(offset_limit=split_data_task)
upload_log_task = upload_log_to_s3(log_filename=log_filename)
remove_temp_file_task = remove_temp_file()

(
    fetch_task
    >> split_data_task
    >> parallel_tasks
    >> [upload_log_task, remove_temp_file_task]
)
