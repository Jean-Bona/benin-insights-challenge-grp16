"""
Dashboard Bénin Insights — Groupe 16
iSHEERO × DataCamp Donates · 2025
Adapté depuis : global-conflict-intelligence-dashboard (Vireen555)

Usage :
    pip install streamlit plotly pydeck pandas
    streamlit run dashboard_benin.py

Données requises (générées par benin_pipeline_complet.ipynb) :
    data/processed/benin_2025_clean.csv
    data/processed/benin_2025_agregat_mensuel.csv
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bénin Insights — Groupe 16",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLING (inspiré du repo global-conflict-intelligence-dashboard)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0,97,74,0.16), transparent 30%),
            radial-gradient(circle at top right, rgba(252,199,0,0.10), transparent 28%),
            radial-gradient(circle at bottom left, rgba(232,17,45,0.08), transparent 25%),
            linear-gradient(135deg, #06131f 0%, #0b1220 45%, #111827 100%);
        color: #e5eef9;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 22px;
        padding: 1.1rem 1.1rem 0.9rem 1.1rem;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.22);
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 0.88rem;
        color: rgba(229, 238, 249, 0.68);
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
    }
    .metric-sub {
        margin-top: 0.3rem;
        font-size: 0.80rem;
        color: rgba(229, 238, 249, 0.55);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.15rem;
        letter-spacing: -0.02em;
    }
    .hero-flag {
        font-size: 2.8rem;
        vertical-align: middle;
        margin-right: 0.3rem;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(229, 238, 249, 0.70);
        margin-bottom: 1.4rem;
    }
    section[data-testid="stSidebar"] {
        background: rgba(8, 15, 26, 0.85);
        border-right: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(14px);
    }
    .insight-box {
        background: linear-gradient(135deg, rgba(0,97,74,0.18), rgba(252,199,0,0.06));
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 22px;
        padding: 1.2rem;
        backdrop-filter: blur(14px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.22);
        margin-bottom: 1rem;
    }
    .insight-label {
        font-size: 0.80rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(229, 238, 249, 0.60);
        margin-bottom: 0.3rem;
    }
    .insight-text {
        font-size: 1rem;
        line-height: 1.65;
        color: #f8fbff;
    }
    .badge-vert { color: #4CAF50; font-weight: bold; }
    .badge-rouge { color: #F44336; font-weight: bold; }
    .badge-jaune { color: #FFC107; font-weight: bold; }
    label, .stMarkdown, .stCaption, .stText {
        color: #e5eef9 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES CAMEO
# ─────────────────────────────────────────────────────────────────────────────
CAMEO_LABELS = {
    1: 'Déclarations publiques', 2: 'Appels / demandes',
    3: "Expressions d'intention", 4: 'Consultations',
    5: 'Engagement diplomatique', 6: 'Coopération matérielle',
    7: 'Aide fournie', 8: 'Céder / coopérer',
    9: 'Médiation', 10: 'Demandes / propositions',
    11: 'Désapprobation', 12: 'Rejet',
    13: 'Menace', 14: 'Protestation',
    15: 'Coercition', 16: 'Attaque militaire',
    17: 'Violence non militaire', 18: 'Assaut',
    19: 'Violence de masse', 20: 'Usage de la force'
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def metric_card(title, value, subtext="", color="#ffffff"):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value" style="color:{color}">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_box(label, text):
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-label">{label}</div>
            <div class="insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_dark():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5eef9"),
        margin=dict(l=10, r=10, t=30, b=10),
    )


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────────────────────────────────────
# ✅ Par ceci (chemin absolu)
CLEAN_PATH   = r"c:\Users\USER\Documents\Hackathon isheero\data\processed\benin_2025_clean.csv"
AGREGAT_PATH = r"c:\Users\USER\Documents\Hackathon isheero\data\processed\benin_2025_agregat_mensuel.csv"

@st.cache_data(ttl=3600)
def load_clean(path):
    df = pd.read_csv(path)

    # ── Colonne date : supporte SQLDATE (YYYYMMDD) ou date (ISO) ─────────────
    if 'date' not in df.columns and 'SQLDATE' in df.columns:
        # SQLDATE peut être YYYYMMDD (entier) ou ISO (après conversion notebook)
        df['date'] = pd.to_datetime(df['SQLDATE'], errors='coerce')
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        raise KeyError("Aucune colonne date ou SQLDATE trouvée dans le CSV.")

    df = df.dropna(subset=['date'])
    df['mois'] = df['date'].dt.strftime('%Y-%m')

    # ── Types numériques ──────────────────────────────────────────────────────
    for col in ['GoldsteinScale', 'AvgTone', 'NumArticles', 'NumMentions',
                'impact_pondere', 'ActionGeo_Lat', 'ActionGeo_Long']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # ── Valeurs manquantes acteurs ────────────────────────────────────────────
    for col in ['Actor1Name', 'Actor2Name', 'Actor1Type1Code', 'Actor2Type1Code']:
        if col in df.columns:
            df[col] = df[col].fillna('Non identifié')

    # ── EventRootCode entier ──────────────────────────────────────────────────
    if 'EventRootCode_int' not in df.columns and 'EventRootCode' in df.columns:
        df['EventRootCode_int'] = pd.to_numeric(
            df['EventRootCode'].astype(str).str[:2], errors='coerce'
        )

    # ── Catégorie CAMEO lisible ───────────────────────────────────────────────
    if 'categorie_event' not in df.columns and 'EventRootCode_int' in df.columns:
        df['categorie_event'] = df['EventRootCode_int'].map(CAMEO_LABELS).fillna('Autre')

    # ── is_violent ────────────────────────────────────────────────────────────
    if 'is_violent' not in df.columns and 'EventRootCode_int' in df.columns:
        df['is_violent'] = df['EventRootCode_int'] >= 13
    elif 'is_violent' in df.columns:
        df['is_violent'] = df['is_violent'].astype(bool)

    # ── type_quadclass ────────────────────────────────────────────────────────
    if 'type_quadclass' not in df.columns and 'QuadClass' in df.columns:
        qmap = {1: 'Coopération verbale', 2: 'Coopération matérielle',
                3: 'Conflit verbal',      4: 'Conflit matériel'}
        df['type_quadclass'] = pd.to_numeric(
            df['QuadClass'], errors='coerce'
        ).map(qmap).fillna('Non classifié')

    # ── zone_geo ──────────────────────────────────────────────────────────────
    if 'zone_geo' not in df.columns and 'ActionGeo_Lat' in df.columns:
        CLAT, CLON, TOL = 9.5, 2.25, 0.15
        def _zone(row):
            lat, lon = row['ActionGeo_Lat'], row['ActionGeo_Long']
            if pd.isna(lat) or pd.isna(lon):
                return 'Non localisé'
            if abs(lat - CLAT) < TOL and abs(lon - CLON) < TOL:
                return 'Non localisé'
            return 'Nord (Atakora / Alibori)' if lat >= 10.0 else 'Sud'
        df['zone_geo'] = df.apply(_zone, axis=1)

    # ── impact_pondere ────────────────────────────────────────────────────────
    if 'impact_pondere' not in df.columns and 'GoldsteinScale' in df.columns:
        df['impact_pondere'] = df['GoldsteinScale'] * np.log(
            df['NumArticles'].fillna(0) + 1
        )

    # ── communaute_linguistique ───────────────────────────────────────────────
    if 'communaute_linguistique' not in df.columns and 'SOURCEURL' in df.columns:
        def _comm(url):
            if pd.isna(url): return 'Autre / Non identifié'
            url = str(url).lower()
            if any(x in url for x in ['.fr/', 'rfi.fr', 'lemonde.fr',
                                        'banouto', 'golfeinfo', '24haubenin']):
                return 'Francophonie'
            if any(x in url for x in ['.ng/', '.gh/', '.ke/', 'bbc.com',
                                        'reuters.com', 'punchng', 'apnews']):
                return 'Commonwealth / Anglophone'
            if any(x in url for x in ['.cn/', 'xinhua', 'chinadaily', 'cgtn']):
                return 'Chine'
            if any(x in url for x in ['.pt/', '.ao/', '.br/', 'voaportugues']):
                return 'Lusophonie'
            return 'Autre / Non identifié'
        df['communaute_linguistique'] = df['SOURCEURL'].apply(_comm)

    # ── source_domain ─────────────────────────────────────────────────────────
    if 'source_domain' not in df.columns and 'SOURCEURL' in df.columns:
        df['source_domain'] = df['SOURCEURL'].str.extract(
            r'https?://(?:www\.)?([^/]+)', expand=False
        )

    return df


@st.cache_data(ttl=3600)
def load_agregat(path):
    df = pd.read_csv(path)
    return df


try:
    df = load_clean(CLEAN_PATH)
    agregat = load_agregat(AGREGAT_PATH)
    DATA_OK = True
except Exception as e:
    DATA_OK = False
    DATA_ERROR = str(e)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — FILTRES
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🇧🇯 Bénin Insights · Groupe 16")
    st.markdown("---")

    if DATA_OK:
        mois_dispo = sorted(df['mois'].dropna().unique().tolist())
        mois_sel = st.multiselect(
            "📅 Période (mois)",
            options=mois_dispo,
            default=mois_dispo,
        )

        zones_dispo = sorted(df['zone_geo'].dropna().unique().tolist()) if 'zone_geo' in df.columns else []
        zones_sel = st.multiselect(
            "🗺️ Zone géographique",
            options=zones_dispo,
            default=zones_dispo,
        )

        quadclasses = sorted(df['type_quadclass'].dropna().unique().tolist()) if 'type_quadclass' in df.columns else []
        quad_sel = st.multiselect(
            "🏷️ Type d'événement",
            options=quadclasses,
            default=quadclasses,
        )

        only_violent = st.checkbox("⚠️ Événements violents uniquement", value=False)

        st.markdown("---")
        st.caption("📌 Données : GDELT BigQuery · 2025")
        st.caption("🏆 Hackathon iSHEERO × DataCamp 2026")

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-title"><span class="hero-flag">🇧🇯</span> Bénin Insights Dashboard</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-subtitle">Analyse GDELT 2025 — Couverture médiatique mondiale des événements béninois · '
    'Groupe 16 · iSHEERO × DataCamp Donates</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# DONNÉES NON CHARGÉES
# ─────────────────────────────────────────────────────────────────────────────
if not DATA_OK:
    st.error(
        f"⚠️ Fichiers de données introuvables. "
        f"Lance d'abord `benin_pipeline_complet.ipynb` pour générer les datasets gold.\n\n"
        f"Erreur : {DATA_ERROR}"
    )
    st.info(
        "**Fichiers requis :**\n"
        "- `data/processed/benin_2025_clean.csv`\n"
        "- `data/processed/benin_2025_agregat_mensuel.csv`"
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# FILTRAGE
# ─────────────────────────────────────────────────────────────────────────────
filt = df.copy()
if mois_sel:
    filt = filt[filt['mois'].isin(mois_sel)]
if zones_sel and 'zone_geo' in filt.columns:
    filt = filt[filt['zone_geo'].isin(zones_sel)]
if quad_sel and 'type_quadclass' in filt.columns:
    filt = filt[filt['type_quadclass'].isin(quad_sel)]
if only_violent and 'is_violent' in filt.columns:
    filt = filt[filt['is_violent'] == True]

if filt.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue d'ensemble",
    "🗺️ Carte géographique",
    "👥 Acteurs & Réseaux",
    "📰 Couverture médiatique",
])

# =============================================================================
# TAB 1 — VUE D'ENSEMBLE
# =============================================================================
with tab1:

    # KPI SUMMARY BOX
    goldstein_moy = filt['GoldsteinScale'].mean()
    ton_moy = filt['AvgTone'].mean()
    pct_violent = filt['is_violent'].mean() * 100 if 'is_violent' in filt.columns else 0
    impact_moy = filt['impact_pondere'].mean() if 'impact_pondere' in filt.columns else 0

    stabilite_label = "🟢 Globalement stable" if goldstein_moy > 0 else "🔴 Période instable"
    ton_label_str = "🟡 Légèrement négatif" if -3 < ton_moy < 0 else ("🔴 Très négatif" if ton_moy <= -3 else "🟢 Positif")

    insight_box(
        "Synthèse de la période analysée",
        f"Le Bénin affiche un score Goldstein moyen de <b>{goldstein_moy:+.2f}</b> — {stabilite_label}. "
        f"Le prisme médiatique international reste <b>{ton_label_str}</b> "
        f"(ton moyen : {ton_moy:.2f}), ce qui est cohérent avec le biais structurellement négatif "
        f"des médias sur l'Afrique subsaharienne. "
        f"<b>{pct_violent:.1f}%</b> des événements sont conflictuels "
        f"(EventRootCode ≥ 13). Score d'impact pondéré moyen : <b>{impact_moy:+.2f}</b>."
    )

    # KPI CARDS
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        metric_card("Événements analysés", f"{len(filt):,}", "Après nettoyage & filtrage")
    with k2:
        color = "#4CAF50" if goldstein_moy > 0 else "#F44336"
        metric_card("Goldstein moyen", f"{goldstein_moy:+.2f}", "Stabilité (-10 → +10)", color=color)
    with k3:
        metric_card("Ton médiatique", f"{ton_moy:.2f}", "AvgTone moyen", color="#FFC107")
    with k4:
        color_v = "#F44336" if pct_violent > 20 else "#FF9800"
        metric_card("% Violents", f"{pct_violent:.1f}%", "EventRootCode ≥ 13", color=color_v)
    with k5:
        metric_card("Impact pondéré", f"{impact_moy:+.2f}", "Goldstein × log(NumArticles+1)")

    st.markdown("---")

    # ROW 1 : Volume mensuel + QuadClass
    r1l, r1r = st.columns([1.6, 1], gap="large")

    with r1l:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Volume d'événements par mois")
        ev_mois = (
            filt.dropna(subset=['date'])
            .assign(mois_dt=lambda d: d['date'].dt.to_period('M').dt.to_timestamp())
            .groupby('mois_dt', as_index=False).size()
            .rename(columns={'mois_dt': 'date', 'size': 'nb'})
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ev_mois['date'], y=ev_mois['nb'],
            fill='tozeroy', fillcolor='rgba(233,30,140,0.15)',
            line=dict(color='#E91E8C', width=2.5),
            mode='lines+markers', marker=dict(size=6, color='#E91E8C'),
            name='Événements'
        ))
        fig.update_layout(
            **plotly_dark(),
            xaxis_title="", yaxis_title="Nombre d'événements",
            showlegend=False, height=280
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r1r:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🏷️ Répartition QuadClass")
        if 'type_quadclass' in filt.columns:
            quad_counts = filt['type_quadclass'].value_counts().reset_index()
            quad_counts.columns = ['type', 'count']
            palette = ['#43A047', '#1E88E5', '#FB8C00', '#E53935']
            fig = px.pie(quad_counts, names='type', values='count',
                         color_discrete_sequence=palette, hole=0.4)
            fig.update_layout(**plotly_dark(), height=280, showlegend=True,
                              legend=dict(font=dict(size=10)))
            fig.update_traces(textposition='inside', textinfo='percent+label',
                              textfont_size=9)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ROW 2 : Ton hebdomadaire + Impact pondéré mensuel
    r2l, r2r = st.columns(2, gap="large")

    with r2l:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📉 Ton médiatique hebdomadaire")
        ton_hebdo = (
            filt.dropna(subset=['date'])
            .assign(semaine=lambda d: d['date'].dt.to_period('W').dt.to_timestamp())
            .groupby('semaine', as_index=False)['AvgTone'].mean()
            .rename(columns={'semaine': 'date'})
        )
        fig = go.Figure()
        fig.add_hrect(y0=0, y1=10, fillcolor="rgba(67,160,71,0.06)", line_width=0)
        fig.add_hrect(y0=-10, y1=0, fillcolor="rgba(229,57,53,0.06)", line_width=0)
        fig.add_trace(go.Scatter(
            x=ton_hebdo['date'], y=ton_hebdo['AvgTone'],
            fill='tozeroy',
            fillcolor=ton_hebdo['AvgTone'].apply(
                lambda v: 'rgba(229,57,53,0.20)' if v < 0 else 'rgba(67,160,71,0.20)'
            ).tolist()[0] if len(ton_hebdo) > 0 else 'rgba(229,57,53,0.20)',
            line=dict(color='#5C6BC0', width=1.8),
            mode='lines', name='Ton'
        ))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.4)")
        fig.update_layout(**plotly_dark(), height=260,
                          xaxis_title="", yaxis_title="AvgTone", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2r:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚖️ Impact pondéré moyen / mois")
        if 'impact_pondere' in filt.columns:
            imp_mois = filt.groupby('mois')['impact_pondere'].mean().reset_index()
            imp_mois.columns = ['mois', 'impact']
            imp_mois['couleur'] = imp_mois['impact'].apply(
                lambda v: '#E53935' if v < 0 else '#43A047'
            )
            fig = go.Figure(go.Bar(
                x=imp_mois['mois'], y=imp_mois['impact'],
                marker_color=imp_mois['couleur'],
                opacity=0.8,
                text=imp_mois['impact'].round(2),
                textposition='outside',
                textfont=dict(size=9)
            ))
            fig.add_hline(y=0, line_color="rgba(255,255,255,0.4)")
            fig.update_layout(**plotly_dark(), height=260,
                              xaxis_title="", yaxis_title="Impact pondéré", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ROW 3 : Top catégories CAMEO + Goldstein par catégorie
    r3l, r3r = st.columns([1.2, 1], gap="large")

    with r3l:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎯 Top 10 types d'événements CAMEO")
        if 'categorie_event' in filt.columns:
            top_cat = filt['categorie_event'].value_counts().head(10).reset_index()
            top_cat.columns = ['categorie', 'count']
            fig = px.bar(top_cat, x='count', y='categorie', orientation='h',
                         color='count', color_continuous_scale='RdPu',
                         text='count')
            fig.update_layout(**plotly_dark(), height=320,
                              xaxis_title="Événements", yaxis_title="",
                              coloraxis_showscale=False, showlegend=False)
            fig.update_traces(textposition='outside', textfont_size=9)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r3r:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Goldstein par type d'événement")
        if 'categorie_event' in filt.columns:
            gold_cat = filt.groupby('categorie_event')['GoldsteinScale'].mean() \
                           .sort_values().reset_index()
            gold_cat.columns = ['categorie', 'goldstein']
            gold_cat['couleur'] = gold_cat['goldstein'].apply(
                lambda v: '#E53935' if v < 0 else '#43A047'
            )
            fig = go.Figure(go.Bar(
                x=gold_cat['goldstein'], y=gold_cat['categorie'],
                orientation='h', marker_color=gold_cat['couleur'],
                opacity=0.8
            ))
            fig.add_vline(x=0, line_color="rgba(255,255,255,0.4)")
            fig.update_layout(**plotly_dark(), height=320,
                              xaxis_title="Goldstein moyen", yaxis_title="",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# TAB 2 — CARTE GÉOGRAPHIQUE
# =============================================================================
with tab2:

    # Contexte géographique
    insight_box(
        "Contexte géographique — Limitation GDELT",
        "⚠️ <b>91% des événements</b> sont positionnés sur le centroïde générique du pays "
        "(9.5°N, 2.25°E) — GDELT ne peut pas localiser précisément la majorité des événements "
        "pour les pays peu couverts. Les <b>9% précisément géolocalisés</b> fournissent les "
        "insights les plus forts : concentration des événements violents dans le "
        "<b>nord (Atakora, Alibori)</b>, cohérent avec la menace jihadiste aux frontières du "
        "Burkina Faso et du Niger."
    )

    # Sélection du mode carte
    map_mode = st.radio(
        "Afficher :",
        ["Tous les événements", "Événements violents uniquement", "Centroïde exclu (géolocalisés précis)"],
        horizontal=True,
    )

    # Préparer les données cartographiques
    df_map = filt.dropna(subset=['ActionGeo_Lat', 'ActionGeo_Long']).copy()

    # Exclure le centroïde générique si demandé
    CENTROIDE_LAT, CENTROIDE_LON, TOL = 9.5, 2.25, 0.15
    mask_centroide = (
        (abs(df_map['ActionGeo_Lat'] - CENTROIDE_LAT) < TOL) &
        (abs(df_map['ActionGeo_Long'] - CENTROIDE_LON) < TOL)
    )

    if map_mode == "Événements violents uniquement" and 'is_violent' in df_map.columns:
        df_map = df_map[df_map['is_violent'] == True]
    elif map_mode == "Centroïde exclu (géolocalisés précis)":
        df_map = df_map[~mask_centroide]

    # Couleur selon QuadClass
    quadclass_colors = {
        'Coopération verbale':     [67, 160, 71],    # vert
        'Coopération matérielle':  [30, 136, 229],   # bleu
        'Conflit verbal':          [251, 140, 0],    # orange
        'Conflit matériel':        [229, 57, 53],    # rouge
        'Non classifié':           [158, 158, 158],  # gris
    }

    df_map['color'] = df_map['type_quadclass'].map(quadclass_colors).apply(
        lambda x: x if isinstance(x, list) else [158, 158, 158]
    )
    df_map['radius'] = df_map['NumArticles'].fillna(1).clip(lower=1)
    df_map['radius'] = (df_map['radius'] * 800 + 8000).clip(8000, 40000)

    ml, mr = st.columns([1.7, 1], gap="large")

    with ml:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader(f"🗺️ Carte des événements ({len(df_map):,} points)")

        if df_map.empty:
            st.info("Aucune coordonnée disponible pour les filtres actuels.")
        else:
            view = pdk.ViewState(
                latitude=9.3, longitude=2.3, zoom=6, pitch=30
            )
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position="[ActionGeo_Long, ActionGeo_Lat]",
                get_fill_color="color",
                get_radius="radius",
                pickable=True,
                opacity=0.75,
                stroked=True,
                filled=True,
                radius_min_pixels=4,
                radius_max_pixels=25,
                line_width_min_pixels=1,
                get_line_color=[255, 255, 255, 60],
            )
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                map_provider="carto",
                map_style="dark",
                tooltip={
                    "html": """
                    <b>{type_quadclass}</b><br/>
                    <b>Lieu :</b> {ActionGeo_FullName}<br/>
                    <b>Acteur 1 :</b> {Actor1Name}<br/>
                    <b>Acteur 2 :</b> {Actor2Name}<br/>
                    <b>Goldstein :</b> {GoldsteinScale}<br/>
                    <b>Articles :</b> {NumArticles}<br/>
                    <b>Zone :</b> {zone_geo}
                    """,
                    "style": {
                        "backgroundColor": "rgba(15,23,42,0.92)",
                        "color": "white",
                        "borderRadius": "12px",
                    },
                },
            )
            st.pydeck_chart(deck, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with mr:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 Top zones conflictuelles")

        if 'zone_geo' in filt.columns:
            zone_stats = filt.groupby('zone_geo').agg(
                nb_ev=('SQLDATE', 'count'),
                goldstein=('GoldsteinScale', 'mean'),
                pct_violent=('is_violent', 'mean'),
                impact=('impact_pondere', 'mean')
            ).reset_index()
            zone_stats['pct_violent'] = (zone_stats['pct_violent'] * 100).round(1)
            zone_stats['goldstein'] = zone_stats['goldstein'].round(2)
            zone_stats['impact'] = zone_stats['impact'].round(2)
            st.dataframe(zone_stats, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🏘️ Top 15 lieux précis")
        if 'ActionGeo_FullName' in filt.columns:
            lieux = filt[filt['ActionGeo_FullName'].notna()]
            lieux = lieux[~lieux['ActionGeo_FullName'].str.lower().str.contains('benin$', na=True)]
            top_lieux = lieux['ActionGeo_FullName'].value_counts().head(15).reset_index()
            top_lieux.columns = ['lieu', 'events']
            fig = px.bar(top_lieux, x='events', y='lieu', orientation='h',
                         color='events', color_continuous_scale='Reds')
            fig.update_layout(**plotly_dark(), height=380,
                              xaxis_title="Événements", yaxis_title="",
                              coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# TAB 3 — ACTEURS & RÉSEAUX
# =============================================================================
with tab3:

    insight_box(
        "Qui agit au Bénin ? — Analyse des acteurs GDELT",
        "Les acteurs sont classifiés par GDELT selon une taxonomie CAMEO : "
        "GOV (gouvernement), MIL (militaire), NGO, REB (rebelles), MED (médias), OPP (opposition)... "
        "Actor1 est l'initiateur de l'action, Actor2 est la cible ou le second acteur. "
        "Les valeurs manquantes (~9.6% Actor1, ~31% Actor2) correspondent aux acteurs non identifiés "
        "— ces NaN sont conservés dans le dataset car ils sont informatifs."
    )

    al, ar = st.columns(2, gap="large")

    with al:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("👤 Top acteurs mentionnés (Actor1 + Actor2)")

        acteurs = pd.concat([
            filt[filt['Actor1Name'] != 'Non identifié']['Actor1Name'],
            filt[filt['Actor2Name'] != 'Non identifié']['Actor2Name']
        ], ignore_index=True).value_counts().head(15).reset_index()
        acteurs.columns = ['acteur', 'mentions']

        fig = px.bar(acteurs, x='mentions', y='acteur', orientation='h',
                     color='mentions', color_continuous_scale='RdPu',
                     text='mentions')
        fig.update_layout(**plotly_dark(), height=420,
                          xaxis_title="Mentions", yaxis_title="",
                          coloraxis_showscale=False)
        fig.update_traces(textposition='outside', textfont_size=9)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ar:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🌍 Pays acteurs (CountryCode)")

        pays = pd.concat([
            filt['Actor1CountryCode'].dropna(),
            filt['Actor2CountryCode'].dropna()
        ], ignore_index=True).value_counts().head(15).reset_index()
        pays.columns = ['pays', 'count']
        # Exclure le Bénin lui-même pour voir les interactions extérieures
        pays = pays[~pays['pays'].isin(['BEN', 'BN'])]

        fig = px.pie(pays, names='pays', values='count',
                     color_discrete_sequence=px.colors.qualitative.Set3,
                     hole=0.35)
        fig.update_layout(**plotly_dark(), height=420,
                          legend=dict(font=dict(size=10)))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=9)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Types d'acteurs
    bt, = st.columns([1])

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🏷️ Nature des acteurs (Type1Code) — Qui fait quoi ?")

    tl, tr = st.columns(2, gap="large")
    with tl:
        st.caption("Actor1 — Initiateurs")
        if 'Actor1Type1Code' in filt.columns:
            t1 = filt[filt['Actor1Type1Code'] != 'Non identifié']['Actor1Type1Code'].value_counts().head(12).reset_index()
            t1.columns = ['type', 'count']
            fig = px.bar(t1, x='count', y='type', orientation='h',
                         color='count', color_continuous_scale='Blues')
            fig.update_layout(**plotly_dark(), height=320,
                              xaxis_title="Occurrences", yaxis_title="",
                              coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with tr:
        st.caption("Actor2 — Cibles / seconds acteurs")
        if 'Actor2Type1Code' in filt.columns:
            t2 = filt[filt['Actor2Type1Code'] != 'Non identifié']['Actor2Type1Code'].value_counts().head(12).reset_index()
            t2.columns = ['type', 'count']
            fig = px.bar(t2, x='count', y='type', orientation='h',
                         color='count', color_continuous_scale='Oranges')
            fig.update_layout(**plotly_dark(), height=320,
                              xaxis_title="Occurrences", yaxis_title="",
                              coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# TAB 4 — COUVERTURE MÉDIATIQUE
# =============================================================================
with tab4:

    insight_box(
        "Analyse de la couverture médiatique mondiale du Bénin",
        "GDELT agrège plus de 100 langues via traduction automatique. "
        "L'<b>AvgTone moyen de -1.50</b> confirme un prisme médiatique structurellement négatif "
        "sur l'Afrique subsaharienne, indépendamment de la nature des événements "
        "(même les événements coopératifs ont un ton moyen de -0.80). "
        "La colonne <i>communauté linguistique</i> permet de quantifier ce biais par communauté."
    )

    m1, m2, m3, m4 = st.columns(4)
    articles_tot = int(filt['NumArticles'].sum()) if 'NumArticles' in filt.columns else 0
    mentions_tot = int(filt['NumMentions'].sum()) if 'NumMentions' in filt.columns else 0
    max_articles = int(filt['NumArticles'].max()) if 'NumArticles' in filt.columns else 0
    nb_domaines = filt['source_domain'].nunique() if 'source_domain' in filt.columns else 0

    with m1:
        metric_card("Articles totaux", f"{articles_tot:,}", "Somme NumArticles")
    with m2:
        metric_card("Mentions totales", f"{mentions_tot:,}", "Somme NumMentions")
    with m3:
        metric_card("Max articles / événement", f"{max_articles:,}", "Événement le + médiatique")
    with m4:
        metric_card("Domaines sources", f"{nb_domaines:,}", "Médias distincts")

    st.markdown("---")

    cl, cr = st.columns([1, 1.3], gap="large")

    with cl:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🌐 Couverture par communauté linguistique")

        if 'communaute_linguistique' in filt.columns:
            comm = filt['communaute_linguistique'].value_counts().reset_index()
            comm.columns = ['communaute', 'count']
            palette_comm = {
                'Francophonie': '#3F51B5',
                'Commonwealth / Anglophone': '#E91E8C',
                'Chine': '#FF6F00',
                'Lusophonie': '#009688',
                'Autre / Non identifié': '#757575',
            }
            colors = [palette_comm.get(c, '#757575') for c in comm['communaute']]
            fig = go.Figure(go.Pie(
                labels=comm['communaute'], values=comm['count'],
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='percent+label',
                textfont_size=10,
            ))
            fig.update_layout(**plotly_dark(), height=320, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Ton moyen par communauté
            st.caption("Ton médiatique moyen par communauté")
            ton_comm = filt.groupby('communaute_linguistique')['AvgTone'].mean().round(2).reset_index()
            ton_comm.columns = ['Communauté', 'Ton moyen']
            ton_comm['Ton'] = ton_comm['Ton moyen'].apply(
                lambda v: f"🔴 {v:.2f}" if v < -2 else f"🟡 {v:.2f}" if v < 0 else f"🟢 {v:.2f}"
            )
            st.dataframe(ton_comm[['Communauté', 'Ton']], use_container_width=True, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📰 Top 20 domaines sources")

        if 'source_domain' in filt.columns:
            domaines = filt['source_domain'].value_counts().head(20).reset_index()
            domaines.columns = ['domaine', 'articles']
            fig = px.bar(domaines, x='articles', y='domaine', orientation='h',
                         color='articles', color_continuous_scale='Magma',
                         text='articles')
            fig.update_layout(**plotly_dark(), height=520,
                              xaxis_title="Articles", yaxis_title="",
                              coloraxis_showscale=False)
            fig.update_traces(textposition='outside', textfont_size=8)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Événements les plus médiatisés
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔥 Top 20 événements les plus médiatisés")

    cols_show = ['date', 'categorie_event', 'type_quadclass', 'zone_geo',
                 'Actor1Name', 'Actor2Name', 'NumArticles', 'GoldsteinScale',
                 'impact_pondere', 'ActionGeo_FullName', 'SOURCEURL']
    cols_ok = [c for c in cols_show if c in filt.columns]

    top20 = filt.nlargest(20, 'NumArticles')[cols_ok].copy()
    if 'date' in top20.columns:
        top20['date'] = pd.to_datetime(top20['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    if 'impact_pondere' in top20.columns:
        top20['impact_pondere'] = top20['impact_pondere'].round(2)
    if 'GoldsteinScale' in top20.columns:
        top20['GoldsteinScale'] = top20['GoldsteinScale'].round(2)

    st.dataframe(top20, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    # Ajouter dans Tab 4 — après le camembert communaute_linguistique
if 'langue' in filt.columns:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🗣️ Ton médiatique par langue de couverture")

    ton_langue = filt.groupby('langue').agg(
        nb_articles = ('NumArticles', 'sum'),
        ton_moyen   = ('AvgTone', 'mean'),
        nb_events   = ('SQLDATE', 'count')
    ).reset_index().sort_values('ton_moyen')

    fig = px.bar(
        ton_langue,
        x='ton_moyen', y='langue',
        orientation='h',
        color='ton_moyen',
        color_continuous_scale='RdYlGn',
        range_color=[-5, 5],
        text=ton_langue['ton_moyen'].round(2),
        size_max=40,
        hover_data={'nb_events': True, 'nb_articles': True}
    )
    fig.add_vline(x=0, line_dash='dot',
                  line_color='rgba(255,255,255,0.5)')
    fig.update_layout(
        **plotly_dark(), height=300,
        xaxis_title='Ton moyen (AvgTone)',
        yaxis_title='',
        coloraxis_showscale=False
    )
    fig.update_traces(textposition='outside', textfont_size=10)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🇧🇯 Bénin Insights Dashboard · Groupe 16 · iSHEERO × DataCamp Donates · 2025 · "
    "Données : GDELT Project (BigQuery) · "
    "Dashboard inspiré de [global-conflict-intelligence-dashboard](https://github.com/Vireen555/global-conflict-intelligence-dashboard)"
)