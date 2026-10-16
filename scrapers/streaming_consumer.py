from kafka import KafkaConsumer
import json
from scraper_utils import save_to_bronze

consumer = KafkaConsumer('auto-annonces', bootstrap_servers=['kafka:9092'],
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))
print("En attente de messages Kafka...")
for msg in consumer:
    annonce = msg.value
    save_to_bronze([annonce], "stream")