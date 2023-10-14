FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing\
        libpq-dev \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install Pipenv
RUN pip install --upgrade pip pipenv

# Install Python dependencies using Pipenv
WORKDIR /data_api
COPY ./data_api/ /data_api/
RUN pipenv install --deploy --ignore-pipfile

# Copy the FastAPI app
COPY ./data_api/ /data_api/


CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging_config.ini"]
