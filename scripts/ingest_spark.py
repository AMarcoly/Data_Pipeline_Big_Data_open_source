spark = SparkSession.builder.appName('ingest_pipeline').master('local[*]').getOrCreate()
df = df.filter(col('id').isNotNull())
"""Placeholder: ingest_spark.py - implement PySpark ingestion here."""
if __name__ == '__main__':
    print('ingest_spark placeholder')
