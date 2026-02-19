import os
import time
import pymysql
from pymongo import MongoClient, UpdateOne
from datetime import datetime, timezone

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_DB = os.getenv("MYSQL_DB", "projectdb")
MYSQL_USER = os.getenv("MYSQL_USER", "project-user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "project-passwd")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "projectdb")
INTERVAL = int(os.getenv("INTERVAL", "10"))


def fetch_stats():
    connector = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True,
    )
    try:
        with connector.cursor() as cursor:
            cursor.execute("""
                SELECT metric,
                       MIN(value) as min_v,
                       MAX(value) as max_v,
                       AVG(value) as avg_v,
                       COUNT(*) as cnt
                FROM readings
                GROUP BY metric
            """)
            rows = cursor.fetchall()
            return rows
    finally:
        connector.close()


def upsert_stats(rows):
    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    column = db["analytics"]

    now = datetime.now(timezone.utc)

    ops = []
    for metric, min_v, max_v, avg_v, count in rows:
        ops.append(
            UpdateOne(
                {"_id": metric},
                {"$set": {
                    "metric": metric,
                    "min": float(min_v) if min_v is not None else None,
                    "max": float(max_v) if max_v is not None else None,
                    "avg": float(avg_v) if avg_v is not None else None,
                    "count": int(count),
                    "updated_at": now.isoformat()
                }},
                upsert=True
            )
        )

    if ops:
        column.bulk_write(ops)
    client.close()


def main():
    print(f"[analytics] starting, interval={INTERVAL}s")
    while True:
        try:
            rows = fetch_stats()
            upsert_stats(rows)
            print(f"[analytics] updated {len(rows)} metric(s)")
        except Exception as e:
            print(f"[analytics] error: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()