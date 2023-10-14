#!/bin/bash

# Initialize the database
airflow db migrate

# Create the admin user
airflow users  create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin

# Run the server
airflow webserver
