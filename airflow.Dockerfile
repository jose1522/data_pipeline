FROM apache/airflow:2.7.2-python3.10

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

USER root

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc python3-dev && \
    apt-get autoremove -y && \
    apt-get clean -y


# Install Pipenv
USER airflow
RUN pip install --upgrade pip pipenv

# Install Python dependencies using Pipenv
WORKDIR /airflow
COPY ./airflow/ /airflow/
RUN pipenv install --deploy --ignore-pipfile
