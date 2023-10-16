# Data Pipeline Coding Challenge

## Overview

This repository contains the codebase for a data pipeline coding challenge that includes Airflow DAGs, API endpoints, and database models.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Airflow DAGs](#airflow-dags)
  - [API Endpoints](#api-endpoints)
- [Testing](#testing)

## Getting Started

### Prerequisites

- Docker
- Python 3.10
- Pipenv

### Installation

1. Clone the repository
   ```
   git clone https://github.com/jose1522/data_pipeline.git
   ```
2. Navigate to the project directory
   ```
   cd data_pipeline
   ```
3. Start the services
   ```
   make start-services
   ```

## Usage

### Airflow DAGs

- `bulk_insert.py`: This is used to bulk insert data into the database. It is triggered manually.
- `database_backup.py`: This is used to backup the database to a file in AVRO format. It is triggered manually.
- `database_restore.py`: This is used to restore the database from a file in AVRO format. It is triggered manually.

### API Endpoints

- `localhost:8000/v1/department`: Supports GET, POST, PUT, and DELETE requests, as well as bulk inserts via POST.
- `localhost:8000/v1/job`: Supports GET, POST, PUT, and DELETE requests, as well as bulk inserts via POST.
- `localhost:8000/v1/user`: Supports GET, POST, PUT, and DELETE requests, as well as bulk inserts via POST.
- `localhost:8000/v1/report`: Supports GET requests. Outputs csv files

## Testing

Make sure you have initialized the virtual environment and installed the dependencies.
```
make create-venv
```

Run the tests using the following command:

```
make run-tests
```
