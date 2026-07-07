# Data Pipeline Big Data Open Source (Spark + SQL)

Objectif
--------
Construire un pipeline d'ingestion et de traitement à grande échelle sur des fichiers CSV volumineux en utilisant Apache Spark, stockage Postgres, orchestration Airflow et visualisation Metabase.

Contenu
-------
- `docker-compose.yml` : services Postgres, Spark (master/worker), Airflow (standalone), Metabase
- `airflow/Dockerfile` : image Airflow avec Java + dépendances Python (pyspark, pandas, psycopg2...)
- `Makefile` : commandes pratiques (up/down/generate/ingest/load/pipeline)
- `requirements.txt` : libs Python nécessaires pour les scripts locaux
- `scripts/generate_data.py` : génère des CSV de commandes e-commerce (avec quelques données sales à nettoyer)
- `scripts/ingest_spark.py` : nettoyage/transformation PySpark, écriture en Parquet partitionné
- `scripts/load_to_postgres.py` : chargement du Parquet nettoyé dans Postgres (table `orders`)
- `airflow/dags/pipeline_dag.py` : DAG orchestrant generate -> ingest -> load
- `sql/queries.sql` : requêtes analytiques (fenêtres, cumuls, classements)

Prérequis
--------
- Docker & Docker Compose installés localement
- Python 3.10+ pour exécuter `generate`/`load` localement (l'ingestion Spark tourne dans le conteneur `spark-master`)

Démarrage rapide
----------------
1. Lancer les services :

```bash
make up
```

Cela démarre : Postgres (`localhost:5432`), Spark master UI (`localhost:8080`), Airflow (`localhost:8081`), Metabase (`localhost:3000`).

2. Installer les dépendances Python locales :

```bash
make venv
```

3. Exécuter le pipeline complet (génération -> ingestion Spark -> chargement Postgres) :

```bash
make pipeline
```

Ou étape par étape : `make generate`, `make ingest`, `make load`.

4. Explorer les données :
- Requêtes SQL prêtes à l'emploi dans `sql/queries.sql` (via `psql` ou l'éditeur SQL de Metabase).
- Dans Metabase (`localhost:3000`), connecter une base "PostgreSQL" avec host `postgres`, port `5432`, base `bigdata`, utilisateur/mot de passe `bigdata`.

5. Orchestration Airflow : le DAG `big_data_pipeline` (visible sur `localhost:8081`) enchaîne les trois mêmes étapes ; identifiants admin générés au premier démarrage visibles dans `docker compose logs airflow`.

Notes
-----
- Configuration minimale pensée pour prototyper en local (Airflow en `SequentialExecutor`/SQLite, un seul worker Spark). Pour la production, adaptez volumes, utilisateurs, secrets et exécuteur Airflow.
- Les identifiants Postgres par défaut (`bigdata`/`bigdata`) sont à changer en dehors d'un usage local.

Roadmap
-------
- Ajouter tests unitaires et intégration
- Ajouter monitoring et alerting dans Airflow
