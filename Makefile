start-services:
	docker compose -f docker-compose.yml -f docker-compose.airflow.yml -f docker-compose.minio.yml up -d

stop-services:
	docker compose -f docker-compose.yml -f docker-compose.airflow.yml -f docker-compose.minio.yml down -v

create-venv:
	cd data_api && pipenv install
	cd ../

remove-venv:
	cd data_api && pipenv --rm

run-tests:
	PYTHONPATH=$PYTHONPATH:./data_api pytest data_api/tests -v

.PHONY: start-services stop-services create-venv remove-venv
