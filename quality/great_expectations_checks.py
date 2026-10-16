import psycopg2
import pandas as pd
from datetime import datetime

DB_CONFIG = {
    "host": "postgres", "port": 5432,
    "database": "auto_warehouse", "user": "admin", "password": "admin",
}

def run_quality_checks():
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql("SELECT * FROM gold_annonces", conn)
    conn.close()

    results = []
    total = len(df)

    def check(name, condition, dimension):
        passed = int(condition.sum())
        failed = total - passed
        rate = round(passed / total * 100, 2) if total > 0 else 0
        status = "✅ PASS" if rate >= 80 else "❌ FAIL"
        results.append({
            "check": name, "dimension": dimension,
            "passed": passed, "failed": failed,
            "rate_%": rate, "status": status,
        })

    # ── Complétude ────────────────────────────────────────────────
    check("Titre non vide",      df["titre"].notna(),      "Complétude")
    check("Prix renseigné",      df["prix"].notna(),       "Complétude")
    check("Source renseignée",   df["source"].notna(),     "Complétude")
    check("URL renseignée",      df["url"].notna(),        "Complétude")

    # ── Validité ──────────────────────────────────────────────────
    check("Prix > 0",            df["prix"] > 0,                   "Validité")
    check("Année valide",        df["annee"].between(1990, 2025),   "Validité")
    check("Kilométrage >= 0",    df["kilometrage"] >= 0,            "Validité")

    # ── Cohérence ─────────────────────────────────────────────────
    check("Prix cohérent (< 5M DH)", df["prix"] < 5_000_000, "Cohérence")
    check("Titre > 5 caractères",    df["titre"].str.len() > 5, "Cohérence")

    # ── Unicité ───────────────────────────────────────────────────
    dup_urls = df["url"].duplicated().sum()
    results.append({
        "check": "URLs uniques", "dimension": "Unicité",
        "passed": total - dup_urls, "failed": dup_urls,
        "rate_%": round((total - dup_urls) / total * 100, 2) if total > 0 else 0,
        "status": "✅ PASS" if dup_urls == 0 else "❌ FAIL",
    })

    report = pd.DataFrame(results)
    print("\n" + "="*60)
    print("       RAPPORT QUALITÉ DES DONNÉES")
    print("="*60)
    print(report.to_string(index=False))
    print(f"\nTotal annonces analysées : {total}")
    print(f"Date du rapport : {datetime.now()}")
    print("="*60)
    return report

if __name__ == "__main__":
    run_quality_checks()