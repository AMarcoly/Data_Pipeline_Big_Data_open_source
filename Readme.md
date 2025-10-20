docker-compose up -d
# Data Pipeline Big Data Open Source (Spark + SQL)

Objectif
--------
Construire un pipeline d'ingestion et de traitement à grande échelle sur des fichiers CSV volumineux en utilisant Apache Spark, stockage Postgres, orchestration Airflow et visualisation Metabase.

Contenu du scaffold
-------------------
- `docker-compose.yml` : services Postgres, Spark (master/worker), Airflow, Metabase (config initiale)
- `Makefile` : commandes pratiques (up/down/generate/ingest/load)
- `requirements.txt` : libs Python nécessaires pour les scripts locaux
- `scripts/` : scripts pour générer des CSV, ingérer avec PySpark, charger vers Postgres
- `airflow/dags/` : DAG d'exemple pour orchestér le pipeline
- `sql/queries.sql` : exemples de requêtes analytiques (fenêtres, agrégations)

Prérequis
--------
- Docker & Docker Compose installés localement
- (Optionnel) Python 3.10+ pour exécuter les scripts hors Airflow

Démarrage rapide
----------------
1. Lancer les services :

```bash
# dans le dossier Data_Pipeline_Big_Data_open_source
docker-compose up -d
```

2. (Optionnel) Installer les dépendances Python si vous voulez exécuter les scripts localement :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Générer des données (exemple) :

```bash
make generate
```

4. Ingérer avec Spark et écrire Parquet :

```bash
make ingest
```

5. Charger dans Postgres :

```bash
make load
```

Notes
-----
- Les images et la configuration Airflow fournis sont minimales pour prototyper en local. Pour une utilisation en production, adaptez les volumes, utilisateurs et variables d'environnement.
- Voir `airflow/dags/pipeline_dag.py` pour le DAG de démonstration.

Roadmap
-------
- Ajouter tests unitaires et intégration
- Automatiser le build Docker des scripts
- Ajouter monitoring et alerting dans Airflow
