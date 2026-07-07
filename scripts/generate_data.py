"""Génère des fichiers CSV volumineux de commandes e-commerce pour le pipeline.

Variables d'environnement :
    NUM_ROWS    nombre total de lignes à générer (défaut 500000)
    NUM_FILES   nombre de fichiers CSV à répartir (défaut 5)
    OUTPUT_DIR  dossier de sortie (défaut data/raw)

Des données volontairement "sales" sont injectées (nulls, doublons, quantités
négatives) pour donner du travail au nettoyage effectué par ingest_spark.py.
"""
import csv
import os
import random
from datetime import date, timedelta

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_ROWS = int(os.environ.get("NUM_ROWS", 500_000))
NUM_FILES = int(os.environ.get("NUM_FILES", 5))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "raw"))

CATEGORIES = ["electronics", "books", "clothing", "home", "toys", "sports", "grocery", "beauty"]
PAYMENT_METHODS = ["credit_card", "paypal", "bank_transfer", "gift_card"]
COUNTRIES = ["FR", "DE", "ES", "IT", "BE", "NL", "PT", "LU"]

START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days

FIELDS = [
    "order_id",
    "customer_id",
    "product_id",
    "product_category",
    "quantity",
    "unit_price",
    "order_date",
    "country",
    "payment_method",
]


def random_order_date() -> str:
    return (START_DATE + timedelta(days=random.randint(0, DATE_RANGE_DAYS))).isoformat()


def make_row(order_id: int) -> dict:
    # ~1% de lignes avec customer_id manquant
    customer_id = "" if random.random() < 0.01 else f"CUST-{random.randint(1, 20000):06d}"
    # ~0.5% de quantités invalides (à filtrer au nettoyage)
    quantity = random.randint(-3, -1) if random.random() < 0.005 else random.randint(1, 10)

    return {
        "order_id": f"ORD-{order_id:08d}",
        "customer_id": customer_id,
        "product_id": f"PROD-{random.randint(1, 5000):05d}",
        "product_category": random.choice(CATEGORIES),
        "quantity": quantity,
        "unit_price": round(random.uniform(2.0, 500.0), 2),
        "order_date": random_order_date(),
        "country": random.choice(COUNTRIES),
        "payment_method": random.choice(PAYMENT_METHODS),
    }


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows_per_file = NUM_ROWS // NUM_FILES
    order_id = 1

    for file_idx in range(NUM_FILES):
        path = os.path.join(OUTPUT_DIR, f"orders_{file_idx:03d}.csv")
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for _ in range(rows_per_file):
                row = make_row(order_id)
                writer.writerow(row)
                # ~0.5% de doublons volontaires (même order_id réécrit juste après)
                if random.random() < 0.005:
                    writer.writerow(row)
                order_id += 1
        print(f"[generate_data] écrit {rows_per_file} lignes -> {path}")

    print(f"[generate_data] terminé : {order_id - 1} commandes réparties sur {NUM_FILES} fichiers dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
