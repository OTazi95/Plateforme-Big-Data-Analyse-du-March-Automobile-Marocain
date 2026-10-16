-- ─── Couche Gold : Annonces enrichies ────────────────────────────
CREATE TABLE IF NOT EXISTS gold_annonces (
    id              SERIAL PRIMARY KEY,
    titre           TEXT,
    marque          VARCHAR(100),
    prix            INTEGER,
    kilometrage     INTEGER,
    annee           INTEGER,
    carburant       VARCHAR(50),
    source          VARCHAR(100),
    url             TEXT UNIQUE,
    localisation    VARCHAR(100),
    langue          VARCHAR(20),
    processed_at    TIMESTAMP
);

-- ─── Prix moyen par marque ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gold_prix_par_marque (
    id          SERIAL PRIMARY KEY,
    marque      VARCHAR(100),
    prix_moyen  FLOAT,
    prix_min    INTEGER,
    prix_max    INTEGER,
    nb_annonces INTEGER,
    updated_at  TIMESTAMP
);

-- ─── Annonces par source ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gold_annonces_par_source (
    id          SERIAL PRIMARY KEY,
    source      VARCHAR(100),
    nb_annonces INTEGER,
    updated_at  TIMESTAMP
);

-- ─── Annonces par carburant ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS gold_annonces_par_carburant (
    id          SERIAL PRIMARY KEY,
    carburant   VARCHAR(50),
    nb_annonces INTEGER,
    updated_at  TIMESTAMP
);

-- ─── Index pour les performances ─────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_annonces_marque ON gold_annonces(marque);
CREATE INDEX IF NOT EXISTS idx_annonces_source ON gold_annonces(source);
CREATE INDEX IF NOT EXISTS idx_annonces_annee  ON gold_annonces(annee);