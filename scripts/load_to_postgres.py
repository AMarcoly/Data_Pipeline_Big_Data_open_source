"""Charge les données Parquet nettoyées dans Postgres.

Variables d'environnement :
    INPUT_DIR       dossier des fichiers Parquet (défaut data/processed)
    POSTGRES_HOST   défaut localhost
    POSTGRES_PORT   défaut 5432
    POSTGRES_DB     défaut bigdata
    POSTGRES_USER   défaut bigdata
    POSTGRES_PASSWORD défaut bigdata
    TABLE_NAME      défaut orders
"""
import os

import pandas as pd
from sqlalchemy import create_engine

INPUT_DIR = os.environ.get("INPUT_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "processed"))
TABLE_NAME = os.environ.get("TABLE_NAME", "orders")

CHUNK_SIZE = 50_000


def build_engine():
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "bigdata")
    user = os.environ.get("POSTGRES_USER", "bigdata")
    password = os.environ.get("POSTGRES_PASSWORD", "bigdata")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def main() -> None:
    engine = build_engine()
    df = pd.read_parquet(INPUT_DIR)
    # Les colonnes de partitionnement Hive (order_year/order_month) sont lues comme
    # des catégories/chaînes par pyarrow : on les recast en entier pour un tri numérique
    # correct côté SQL (fonctions fenêtre ORDER BY, GROUP BY, etc.).
    df["order_year"] = df["order_year"].astype(int)
    df["order_month"] = df["order_month"].astype(int)
    total_rows = len(df)
    print(f"[load_to_postgres] {total_rows} lignes lues depuis {INPUT_DIR}")

    first_chunk = True
    for start in range(0, total_rows, CHUNK_SIZE):
        chunk = df.iloc[start : start + CHUNK_SIZE]
        chunk.to_sql(
            TABLE_NAME,
            engine,
            if_exists="replace" if first_chunk else "append",
            index=False,
            method="multi",
        )
        first_chunk = False
        print(f"[load_to_postgres] {min(start + CHUNK_SIZE, total_rows)}/{total_rows} lignes chargées")

    print(f"[load_to_postgres] terminé : table '{TABLE_NAME}' peuplée avec {total_rows} lignes")


if __name__ == "__main__":
    main()
