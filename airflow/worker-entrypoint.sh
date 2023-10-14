#!/bin/bash

# Initialize the database
airflow db migrate
airflow scheduler
