# Plateforme Big Data — Analyse du Marché Automobile Marocain

## Problématique
Comment analyser les tendances du marché automobile au Maroc à partir des annonces
en ligne (Avito.ma), afin d'identifier les modèles les plus populaires, l'évolution
des prix et les caractéristiques les plus recherchées ?

## Étudiants
- Étudiant 1 : Mr Omar Tazi
- Étudiant 2 : Mlle Meriam Erragragui
- Étudiant 3 : Mme Wissal Lmhal


## Architecture
Avito.ma (Scraping)
↓
Kafka (Streaming) ──→ Bronze (MinIO)
Airflow (Batch)   ──→ Bronze (MinIO)
↓
Silver (MinIO) — Nettoyage + Normalisation
↓
Gold (PostgreSQL) — Tables analytiques
↓
Dashboard (Streamlit)

## Technologies utilisées

| Composant | Technologie |
|---|---|
| Scraping | Python, BeautifulSoup |
| Streaming | Apache Kafka |
| Orchestration | Apache Airflow |
| Data Lake | MinIO (S3-compatible) |
| Transformations | Python, Pandas |
| Data Warehouse | PostgreSQL |
| Visualisation | Streamlit, Plotly |
| Conteneurisation | Docker, Docker Compose |

## Prérequis
- Docker Desktop installé et démarré
- Au moins 8 GB de RAM disponible
- Au moins 10 GB d'espace disque libre
- Ports disponibles : 8085, 8501, 9000, 9001, 5432, 9092

## Lancement du projet

### 1. Cloner / extraire le projet
```bash
cd prj_data_auto
```

### 2. Lancer tous les services
```bash
docker-compose up --build -d
```
Attendre 2-3 minutes que tous les services démarrent.

### 3. Vérifier que tout tourne
```bash
docker-compose ps
```
Les 9 conteneurs doivent être en statut `Up` :
- minio
- zookeeper
- kafka
- postgres_dw
- postgres_airflow
- airflow
- spark
- scraper
- dashboard

## Utilisation

### Lancer le scraping (collecte Bronze)
```bash
docker exec scraper python avito_scraper.py
docker exec scraper python wandaloo_scraper.py
```

### Lancer les transformations (Silver → Gold)
```bash
docker exec spark python /opt/spark-jobs/bronze_to_silver.py
docker exec spark python /opt/spark-jobs/silver_to_gold.py
```

### Vérifier la qualité des données
```bash
docker exec spark python /opt/quality/great_expectations_checks.py
```

### Lancer le streaming Kafka
```bash
docker cp kafka/producer.py scraper:/app/producer.py
docker exec -it scraper python /app/producer.py
```

## Interfaces web

| Interface | URL | Login |
|---|---|---|
| Airflow (Orchestration) | http://localhost:8085 | admin / admin |
| MinIO (Data Lake) | http://localhost:9001 | minioadmin / minioadmin |
| Dashboard Streamlit | http://localhost:8501 | — |

## Architecture Médaillon

### 🥉 Bronze — Données brutes
- Stockage : MinIO bucket `bronze`
- Format : JSON
- Contenu : Annonces brutes telles que collectées

### 🥈 Silver — Données nettoyées
- Stockage : MinIO bucket `silver`
- Format : CSV
- Transformations :
  - Suppression des doublons
  - Extraction de la marque
  - Nettoyage des prix et kilométrages
  - Détection de la langue
  - Normalisation du texte

### 🥇 Gold — Données analytiques
- Stockage : PostgreSQL (Data Warehouse)
- Tables :
  - `gold_annonces` — Toutes les annonces enrichies
  - `gold_prix_par_marque` — Prix moyen/min/max par marque
  - `gold_annonces_par_source` — Nombre d'annonces par source
  - `gold_annonces_par_carburant` — Répartition par carburant

## Qualité des données
10 contrôles automatisés couvrant 4 dimensions :
- **Complétude** : titre, prix, source, URL renseignés
- **Validité** : prix > 0, année entre 1990-2025, km >= 0
- **Cohérence** : prix < 5M DH, titre > 5 caractères
- **Unicité** : URLs uniques

## Gouvernance
Traçabilité complète du pipeline via la table `data_lineage` dans PostgreSQL,
enregistrant pour chaque transformation : source, destination, nombre d'enregistrements,
statut et timestamp.

## Structure du projet
prj_data_auto/
├── docker-compose.yml       # Orchestration des services
├── README.md                # Ce fichier
├── scrapers/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── avito_scraper.py     # Scraper Avito.ma
│   ├── wandaloo_scraper.py  # Scraper Wandaloo.com
│   └── scraper_utils.py     # Utilitaires MinIO
├── airflow/
│   ├── Dockerfile
│   └── dags/
│       ├── batch_scraping_dag.py    # DAG scraping toutes les heures
│       └── medallion_pipeline_dag.py # DAG Bronze→Silver→Gold
├── spark/
│   ├── Dockerfile
│   ├── bronze_to_silver.py  # Transformation Bronze→Silver
│   └── silver_to_gold.py    # Transformation Silver→Gold
├── kafka/
│   └── producer.py          # Producer streaming Kafka
├── warehouse/
│   └── init.sql             # Schéma du Data Warehouse
├── quality/
│   └── great_expectations_checks.py  # Contrôles qualité
├── governance/
│   └── lineage_logger.py    # Traçabilité des données
└── dashboard/
└── dashboard.py         # Dashboard Streamlit

## Arrêter le projet
```bash
docker-compose down
```

Pour supprimer aussi les données :
```bash
docker-compose down -v
```