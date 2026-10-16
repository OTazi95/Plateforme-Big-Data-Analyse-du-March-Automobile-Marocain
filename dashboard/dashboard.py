import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🚗 Auto Market Analytics", layout="wide")

DB_CONFIG = {
    "host": "postgres", "port": 5432,
    "database": "auto_warehouse", "user": "admin", "password": "admin",
}

@st.cache_data(ttl=300)
def load_data(query):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ── Header ────────────────────────────────────────────────────────
st.title("🚗 Tableau de Bord — Marché Automobile Marocain")
st.markdown("Analyse des tendances à partir des annonces collectées en temps réel")

# ── KPIs ──────────────────────────────────────────────────────────
df_all = load_data("SELECT * FROM gold_annonces")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Annonces",     len(df_all))
col2.metric("Prix Moyen (DH)",    f"{df_all['prix'].mean():,.0f}" if not df_all.empty else "N/A")
col3.metric("Marques Distinctes", df_all["marque"].nunique() if not df_all.empty else 0)
col4.metric("Sources",            df_all["source"].nunique() if not df_all.empty else 0)

st.divider()

# ── Graphiques ────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("💰 Prix Moyen par Marque")
    df_prix = load_data(
        "SELECT marque, prix_moyen, nb_annonces FROM gold_prix_par_marque ORDER BY prix_moyen DESC LIMIT 15"
    )
    if not df_prix.empty:
        fig = px.bar(df_prix, x="marque", y="prix_moyen",
                     color="nb_annonces", color_continuous_scale="Blues",
                     labels={"prix_moyen": "Prix moyen (DH)", "marque": "Marque"})
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("📊 Annonces par Source")
    df_src = load_data("SELECT source, nb_annonces FROM gold_annonces_par_source")
    if not df_src.empty:
        fig2 = px.pie(df_src, names="source", values="nb_annonces",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("⛽ Répartition par Carburant")
    df_carb = load_data("SELECT carburant, nb_annonces FROM gold_annonces_par_carburant")
    if not df_carb.empty:
        fig3 = px.bar(df_carb, x="carburant", y="nb_annonces",
                      color="carburant", labels={"nb_annonces": "Nombre d'annonces"})
        st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("📅 Distribution des Années")
    if not df_all.empty and "annee" in df_all.columns:
        df_annee = df_all["annee"].dropna().astype(int)
        fig4 = px.histogram(df_annee, x="annee", nbins=20,
                            labels={"annee": "Année", "count": "Nombre"})
        st.plotly_chart(fig4, use_container_width=True)

# ── Table des dernières annonces ──────────────────────────────────
st.subheader("🔍 Dernières Annonces Collectées")
df_recent = load_data(
    "SELECT titre, marque, prix, kilometrage, annee, carburant, source, localisation FROM gold_annonces ORDER BY id DESC LIMIT 50"
)
st.dataframe(df_recent, use_container_width=True)