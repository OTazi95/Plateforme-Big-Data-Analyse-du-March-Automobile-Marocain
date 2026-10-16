import boto3
import json
import re
import pandas as pd
from langdetect import detect
from datetime import datetime
import io

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS = "minioadmin"
MINIO_SECRET = "minioadmin"

def get_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS,
        aws_secret_access_key=MINIO_SECRET,
    )

def ensure_bucket(client, bucket):
    try:
        client.head_bucket(Bucket=bucket)
    except:
        client.create_bucket(Bucket=bucket)

def clean_price(price_str):
    """Extrait le prix numérique"""
    if not price_str:
        return None
    digits = re.sub(r"[^\d]", "", str(price_str))
    return int(digits) if digits else None

def clean_km(km_str):
    """Extrait les kilomètres"""
    if not km_str:
        return None
    digits = re.sub(r"[^\d]", "", str(km_str))
    return int(digits) if digits else None

def extract_marque(titre):
    """Détecte la marque depuis le titre"""
    marques = ["Dacia", "Renault", "Volkswagen", "Toyota", "Hyundai",
               "Ford", "BMW", "Mercedes", "Peugeot", "Citroën",
               "Seat", "Skoda", "Audi", "Fiat", "Kia", "Nissan",
               "Honda", "Suzuki", "Mitsubishi", "Mazda"]
    if titre:
        for m in marques:
            if m.lower() in titre.lower():
                return m
    return "Autre"

def transform_bronze_to_silver():
    client = get_client()
    ensure_bucket(client, "silver")

    # Lire tous les fichiers bronze
    response = client.list_objects_v2(Bucket="bronze", Prefix="auto/")
    if "Contents" not in response:
        print("⚠️ Aucun fichier bronze trouvé")
        return

    all_articles = []
    for obj in response["Contents"]:
        key = obj["Key"]
        raw = client.get_object(Bucket="bronze", Key=key)
        data = json.loads(raw["Body"].read().decode("utf-8"))
        all_articles.extend(data)

    print(f"📥 {len(all_articles)} annonces brutes chargées")
    df = pd.DataFrame(all_articles)

    # ── Nettoyage ──────────────────────────────────────────────────
    # 1. Supprimer les doublons
    if 'url' in df.columns:
      df = df.drop_duplicates(subset=["url"], keep="last")
    else:
    # Si pas d'URL, on utilise une combinaison titre + source + scraped_at
      df['_tmp_id'] = df['titre'].astype(str) + '|' + df['source'].astype(str) + '|' + df['scraped_at'].astype(str)
      df = df.drop_duplicates(subset=['_tmp_id'], keep='last')
      df = df.drop(columns=['_tmp_id'])

    # 2. Supprimer les annonces sans titre
    df = df[df["titre"].notna() & (df["titre"] != "")]

    # 3. Nettoyer les prix
    df["prix_clean"] = df["prix"].apply(clean_price)

    # 4. Nettoyer les km
    df["km_clean"] = df["kilometrage"].apply(clean_km) if "kilometrage" in df.columns else None

    # 5. Extraire la marque
    df["marque"] = df["titre"].apply(extract_marque)

    # 6. Normaliser le texte (minuscules, sans espaces multiples)
    df["titre_norm"] = df["titre"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True)

    # 7. Détection de la langue du titre
    def detect_lang(text):
        try:
            return detect(str(text))
        except:
            return "unknown"
    df["langue"] = df["titre_norm"].apply(detect_lang)

    # 8. Timestamp de traitement
    df["processed_at"] = datetime.now().isoformat()

    # ── Sauvegarder en Silver ──────────────────────────────────────
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    client.put_object(
        Bucket="silver",
        Key=f"auto/silver_{timestamp}.csv",
        Body=csv_buffer.getvalue().encode("utf-8"),
        ContentType="text/csv",
    )
    print(f"✅ Silver: {len(df)} annonces nettoyées sauvegardées")
    return df

if __name__ == "__main__":
    transform_bronze_to_silver()