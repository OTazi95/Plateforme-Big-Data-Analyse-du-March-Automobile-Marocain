import boto3
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import io

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS = "minioadmin"
MINIO_SECRET = "minioadmin"

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "auto_warehouse",
    "user": "admin",
    "password": "admin",
}

def get_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS,
        aws_secret_access_key=MINIO_SECRET,
    )

def load_silver():
    client = get_client()
    response = client.list_objects_v2(Bucket="silver", Prefix="")
    if "Contents" not in response:
        return pd.DataFrame()
    dfs = []
    for obj in response["Contents"]:
        raw = client.get_object(Bucket="silver", Key=obj["Key"])
        df = pd.read_csv(io.StringIO(raw["Body"].read().decode("utf-8")))
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def build_gold_tables(df):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ── Gold Table 1 : Annonces enrichies ─────────────────────────
    insert_annonces = """
        INSERT INTO gold_annonces (titre, marque, prix, kilometrage, annee,
                                    carburant, source, url, localisation,
                                    langue, processed_at)
        VALUES %s ON CONFLICT (url) DO NOTHING
    """
    rows = []
    for _, row in df.iterrows():
        rows.append((
            row.get("titre"), row.get("marque"),
            row.get("prix_clean"), row.get("km_clean"),
            row.get("annee"), row.get("carburant"),
            row.get("source"), row.get("url"),
            row.get("localisation"), row.get("langue"),
            row.get("processed_at"),
        ))
    if rows:
        execute_values(cur, insert_annonces, rows)

    # ── Gold Table 2 : Prix moyen par marque ─────────────────────
    cur.execute("DELETE FROM gold_prix_par_marque")
    prix_marque = (
        df.groupby("marque")["prix_clean"]
        .agg(["mean", "min", "max", "count"])
        .reset_index()
        .rename(columns={"mean": "prix_moyen", "min": "prix_min",
                          "max": "prix_max", "count": "nb_annonces"})
    )
    for _, row in prix_marque.iterrows():
        cur.execute(
            """INSERT INTO gold_prix_par_marque
               (marque, prix_moyen, prix_min, prix_max, nb_annonces, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (row["marque"], row["prix_moyen"], row["prix_min"],
             row["prix_max"], row["nb_annonces"], datetime.now()),
        )

    # ── Gold Table 3 : Annonces par source ───────────────────────
    cur.execute("DELETE FROM gold_annonces_par_source")
    par_source = df.groupby("source").size().reset_index(name="nb_annonces")
    for _, row in par_source.iterrows():
        cur.execute(
            "INSERT INTO gold_annonces_par_source (source, nb_annonces, updated_at) VALUES (%s,%s,%s)",
            (row["source"], row["nb_annonces"], datetime.now()),
        )

    # ── Gold Table 4 : Annonces par carburant ────────────────────
    cur.execute("DELETE FROM gold_annonces_par_carburant")
    par_carb = df.groupby("carburant").size().reset_index(name="nb_annonces")
    for _, row in par_carb.iterrows():
        cur.execute(
            "INSERT INTO gold_annonces_par_carburant (carburant, nb_annonces, updated_at) VALUES (%s,%s,%s)",
            (row.get("carburant", "Inconnu"), row["nb_annonces"], datetime.now()),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Gold: tables analytiques mises à jour dans le Data Warehouse")

if __name__ == "__main__":
    df = load_silver()
    if not df.empty:
        build_gold_tables(df)
    else:
        print("⚠️ Pas de données Silver disponibles")