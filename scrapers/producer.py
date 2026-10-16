from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

MARQUES = ["Dacia", "Renault", "Volkswagen", "Toyota", "Hyundai", "Ford", "BMW", "Mercedes"]
MODELES = {
    "Dacia": ["Sandero", "Logan", "Duster"],
    "Renault": ["Clio", "Megane", "Kadjar"],
    "Volkswagen": ["Golf", "Polo", "Passat"],
    "Toyota": ["Yaris", "Corolla", "RAV4"],
    "Hyundai": ["i20", "i30", "Tucson"],
    "Ford": ["Fiesta", "Focus", "Kuga"],
    "BMW": ["Serie 3", "Serie 5", "X3"],
    "Mercedes": ["Classe A", "Classe C", "GLC"],
}

def generate_annonce():
    marque = random.choice(MARQUES)
    modele = random.choice(MODELES[marque])
    return {
        "source": "streaming_feed",
        "titre": f"{marque} {modele}",
        "marque": marque,
        "modele": modele,
        "prix": random.randint(30000, 500000),
        "annee": random.randint(2010, 2024),
        "kilometrage": random.randint(0, 300000),
        "carburant": random.choice(["Essence", "Diesel", "Hybride", "Électrique"]),
        "boite": random.choice(["Manuelle", "Automatique"]),
        "localisation": random.choice(["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger"]),
        "scraped_at": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    print("🚀 Démarrage du producer Kafka...")
    while True:
        annonce = generate_annonce()
        producer.send("auto-annonces", annonce)
        print(f"📤 Envoyé: {annonce['titre']} — {annonce['prix']} DH")
        time.sleep(2)