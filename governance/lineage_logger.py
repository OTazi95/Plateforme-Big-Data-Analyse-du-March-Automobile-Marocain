import psycopg2
from datetime import datetime

DB_CONFIG = {
    "host": "postgres", "port": 5432,
    "database": "auto_warehouse", "user": "admin", "password": "admin",
}

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS data_lineage (
    id          SERIAL PRIMARY KEY,
    pipeline    VARCHAR(100),
    source      VARCHAR(200),
    destination VARCHAR(200),
    nb_records  INTEGER,
    status      VARCHAR(50),
    message     TEXT,
    executed_at TIMESTAMP DEFAULT NOW()
);
"""

def log_lineage(pipeline, source, destination, nb_records, status, message=""):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(CREATE_TABLE)
    cur.execute(
        """INSERT INTO data_lineage (pipeline, source, destination, nb_records, status, message)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (pipeline, source, destination, nb_records, status, message),
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"📝 Lignage enregistré: [{pipeline}] {source} → {destination} | {nb_records} enreg. | {status}")

# Exemple d'utilisation dans les scripts de transformation :
# from governance.lineage_logger import log_lineage
# log_lineage("bronze_to_silver", "minio/bronze/auto/", "minio/silver/auto/", 1500, "SUCCESS")