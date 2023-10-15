#!/bin/bash

rm /airflow/airflow-worker.pid

airflow celery worker
