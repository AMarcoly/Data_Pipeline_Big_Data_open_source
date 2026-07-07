.PHONY: help up down logs ps venv generate ingest load pipeline clean

help:
	@echo "Cibles disponibles :"
	@echo "  up        - démarre postgres/spark/airflow/metabase (docker compose)"
	@echo "  down      - arrête et supprime les conteneurs"
	@echo "  logs      - suit les logs de tous les services"
	@echo "  venv      - crée un virtualenv local et installe requirements.txt"
	@echo "  generate  - génère les CSV bruts (scripts/generate_data.py)"
	@echo "  ingest    - lance l'ingestion Spark sur le cluster (spark-master)"
	@echo "  load      - charge le Parquet nettoyé dans Postgres"
	@echo "  pipeline  - enchaîne generate -> ingest -> load"
	@echo "  clean     - supprime les données générées localement"

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

generate:
	.venv/bin/python scripts/generate_data.py

ingest:
	docker compose exec spark-master spark-submit /opt/scripts/ingest_spark.py

load:
	.venv/bin/python scripts/load_to_postgres.py

pipeline: generate ingest load

clean:
	rm -f data/raw/*.csv
	rm -rf data/processed/*
