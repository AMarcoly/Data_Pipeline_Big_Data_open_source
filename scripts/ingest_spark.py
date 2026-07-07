"""Ingestion PySpark : lit les CSV bruts, nettoie et écrit du Parquet partitionné.

Variables d'environnement :
    INPUT_DIR   dossier des CSV bruts (défaut data/raw, ou /opt/data/raw dans les conteneurs)
    OUTPUT_DIR  dossier de sortie Parquet (défaut data/processed)
"""
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
)

INPUT_DIR = os.environ.get("INPUT_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "raw"))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "processed"))

SCHEMA = StructType(
    [
        StructField("order_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("product_category", StringType(), True),
        StructField("quantity", StringType(), True),
        StructField("unit_price", StringType(), True),
        StructField("order_date", StringType(), True),
        StructField("country", StringType(), True),
        StructField("payment_method", StringType(), True),
    ]
)


def main() -> None:
    spark = SparkSession.builder.appName("ingest_pipeline").master(os.environ.get("SPARK_MASTER", "local[*]")).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    raw = spark.read.csv(f"{INPUT_DIR}/*.csv", header=True, schema=SCHEMA)
    raw_count = raw.count()

    cleaned = (
        raw.withColumn("quantity", F.col("quantity").cast("int"))
        .withColumn("unit_price", F.col("unit_price").cast("double"))
        .withColumn("order_date", F.to_date("order_date"))
        .filter(F.col("order_id").isNotNull())
        .filter(F.col("customer_id").isNotNull())
        .filter(F.col("quantity") > 0)
        .filter(F.col("unit_price") > 0)
        .dropDuplicates(["order_id"])
        .withColumn("total_amount", F.round(F.col("quantity") * F.col("unit_price"), 2))
        .withColumn("order_year", F.year("order_date"))
        .withColumn("order_month", F.month("order_date"))
    )

    clean_count = cleaned.count()

    cleaned.write.mode("overwrite").partitionBy("order_year", "order_month").parquet(OUTPUT_DIR)

    print(f"[ingest_spark] lignes brutes lues     : {raw_count}")
    print(f"[ingest_spark] lignes après nettoyage : {clean_count} ({raw_count - clean_count} rejetées/dédupliquées)")
    print(f"[ingest_spark] parquet écrit dans      : {OUTPUT_DIR}")

    spark.stop()


if __name__ == "__main__":
    main()
