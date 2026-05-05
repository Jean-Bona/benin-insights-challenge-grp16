# Benin Insights Challenge — Groupe 16

> Transformer les données médiatiques mondiales en connaissance locale sur le Bénin.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://benin-insights-challenge-grp16-jdzixsnnddw6zxn24en6kl.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![GDELT](https://img.shields.io/badge/Source-GDELT%20BigQuery-orange)
![Hackathon](https://img.shields.io/badge/iSHEERO-Hackathon%202026-purple)

---

## Dashboard en ligne

**[Acceder au dashboard interactif](https://benin-insights-challenge-grp16-jdzixsnnddw6zxn24en6kl.streamlit.app/)**

Le dashboard est accessible publiquement sans installation.
Il regroupe toutes les visualisations, les modèles ML et le système d'alerte IRP.

---

## Contexte

Ce projet a été réalisé dans le cadre du **Hackathon iSHEERO × DataCamp Donates 2026 — Benin Insights Challenge**.

**Mission :** extraire et analyser les événements GDELT concernant le Bénin
sur l'année 2025, et en faire des insights utiles pour un journaliste,
un chercheur ou un décideur public.

**Source de données :** [GDELT (Global Database of Events, Language and Tone)](https://www.gdeltproject.org/)
— base de données publique qui surveille en temps réel les médias du monde
entier dans plus de 100 langues. Données extraites via Google BigQuery.

---

## Structure du dépôt

```
benin-insights-challenge-grp16/
│
├── dashboard/
│   └── app.py                          # Application Streamlit
│
├── data/
│   ├── raw/                            # Données brutes BigQuery (gitignorées)
│   └── processed/
│       ├── benin_2025_clean.csv        # Dataset nettoyé et enrichi (23 461 lignes)
│       └── benin_2025_agregat_mensuel.csv  # Agrégat mensuel (36 lignes)
│
├── notebooks/
│   ├── 01_pipeline_gdelt.ipynb         # Pipeline extraction → nettoyage → enrichissement
│   ├── eda/
│   │   └── eda.ipynb                   # EDA officielle + modèles ML
│   └── perso/
│       └── eda_bona.ipynb              # EDA individuelle (chef d'équipe)
│
├── reports/                            # Visualisations exportées (.png, .html)
├── models/                             # Modèles entraînés
├── environment.yml                     # Environnement Anaconda reproductible
├── requirements.txt                    # Dépendances pip
└── README.md
```

---

## Installation & Reproduction

### Prérequis

- Anaconda (Python 3.10+)
- Git
- Compte Google (pour BigQuery — 1 TB gratuit/mois)

### Mise en place

```bash
# 1. Cloner le dépôt
git clone https://github.com/Jean-Bona/benin-insights-challenge-grp16.git
cd benin-insights-challenge-grp16

# 2. Créer l'environnement
conda env create -f environment.yml
conda activate benin-insights

# 3. Lancer Jupyter
jupyter notebook
```

### Reproduire le pipeline complet

**Étape 1 — Extraire les données depuis BigQuery**

Exécuter la requête suivante dans [console.cloud.google.com](https://console.cloud.google.com) :

```sql
SELECT
  SQLDATE, EventCode, EventBaseCode, EventRootCode, QuadClass,
  Actor1Name, Actor1CountryCode, Actor1Type1Code,
  Actor2Name, Actor2CountryCode, Actor2Type1Code,
  ActionGeo_FullName, ActionGeo_Lat, ActionGeo_Long,
  GoldsteinScale, NumMentions, NumArticles, AvgTone, SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR = 2025
```

Exporter en CSV dans `data/raw/gdelt_benin_2025_raw.csv`.

**Étape 2 — Lancer le pipeline**

Ouvrir et exécuter `notebooks/01_pipeline_gdelt.ipynb` (Kernel > Restart & Run All).
Produit automatiquement les deux fichiers dans `data/processed/`.

**Étape 3 — Lancer l'analyse**

Ouvrir et exécuter `notebooks/eda/eda.ipynb` (Kernel > Restart & Run All).
Contient l'EDA complète + Random Forest + Isolation Forest + IRP.

**Étape 4 — Lancer le dashboard**

```bash
cd dashboard
streamlit run app.py
```

---

## Les 5 Insights Clés

### 1. Le Bénin est stable en apparence, fracturé en réalité
Les indicateurs nationaux affichent une stabilité globale (Goldstein moyen +0.54).
Mais cette moyenne cache une réalité géographique radicalement différente :
le nord du pays (Atakora, Alibori) enregistre **40% d'événements violents**
contre seulement **12% pour le sud**. Un décideur qui ne regarde que
les chiffres nationaux est trompé sur la situation réelle du terrain.

### 2. Décembre 2025 : la démocratie béninoise sous les projecteurs
La tentative de coup d'état du 7 décembre 2025 a déclenché
le plus grand pic médiatique de l'année — **4 144 événements en un seul mois**,
soit le double de la moyenne mensuelle. Le Bénin étant reconnu
comme un modèle démocratique en Afrique de l'Ouest,
cet événement a suscité un intérêt international exceptionnel.
**Notre système d'alerte l'aurait détecté automatiquement.**

### 3. Les médias internationaux couvrent le Bénin négativement, même quand il coopère
**60.5% des articles** couvrent le Bénin avec un ton négatif —
y compris pour des événements de coopération et de diplomatie
(ton moyen des événements coopératifs : -0.80).
Ce biais structurel est indépendant de ce qui se passe réellement
et reflète le prisme pessimiste des médias internationaux
sur l'Afrique subsaharienne.

### 4. Avril 2025 : le mois le plus dangereux, le moins médiatisé
Avril 2025 présente le taux de violence le plus élevé dans le nord (61.6%)
et l'impact pondéré le plus négatif de l'année (-10.08).
Pourtant, ce mois passe presque inaperçu dans les médias internationaux
— la menace jihadiste au nord est **structurellement sous-médiatisée**
par rapport à son intensité réelle sur le terrain.

### 5. 8 zones du nord nécessitent une attention immédiate
Notre analyse géographique identifie **8 zones en ALERTE** —
toutes dans les départements de l'Alibori et de l'Atakora,
aux frontières du Burkina Faso et du Niger.
Peul (Alibori), Banikoara et Tanougou concentrent
les événements les plus graves de l'année.

---

## Modèles Machine Learning

### Random Forest — Classification de la violence

Prédit si un événement GDELT sera violent à partir
de ses caractéristiques observables (acteurs, ton médiatique, zone, mois).

| Métrique | Valeur |
|----------|--------|
| AUC-ROC | 0.780 |
| F1 violent | 0.454 |
| Recall violent | 51.9% |
| CV F1 moyen | 0.421 ± 0.092 |

**Features principales :** AvgTone (0.328), AvgTone² (0.161),
communauté linguistique (0.121), ratio articles/mentions (0.087).

### Isolation Forest — Détection d'anomalies temporelles

Détecte automatiquement les périodes anormales sans supervision.

| Résultat | Valeur |
|----------|--------|
| Anomalies détectées | 4 / 36 observations |
| Crises réelles détectées | 3 / 3 (recall 100%) |
| Backtesting décembre | Détecté sans avoir vu décembre |

### Indice de Risque Pays (IRP)

Score mensuel unifié combinant les deux modèles :

```
IRP = 0.4 × P(violent | RF) + 0.4 × Anomalie_IF + 0.2 × % violent observé
```

| Mois | IRP | Niveau | Contexte |
|------|-----|--------|----------|
| Avril 2025 | 0.717 | ALERTE | Pic attaques terroristes nord |
| Décembre 2025 | 0.675 | ALERTE | Tentative de coup d'état |
| Janvier 2025 | 0.554 | VIGILANCE | Attaques nord début d'année |
| Mars 2025 | 0.489 | VIGILANCE | Violence diffuse nord |

---

## Pipeline de données

```
BigQuery (GDELT brut, 23 859 lignes)
         ↓
Filtrage temporel strict (YEAR = 2025)
         ↓
Suppression doublons (398 supprimés)
         ↓
Gestion valeurs manquantes
         ↓
Enrichissement (7 colonnes dérivées)
         ↓
Dataset gold : 23 461 lignes · 26 colonnes
         ↓
benin_2025_clean.csv + benin_2025_agregat_mensuel.csv
```

**Colonnes dérivées créées :**
`mois`, `zone_geo`, `type_quadclass`, `is_violent`,
`impact_pondere`, `source_domain`, `communaute_linguistique`

---

## Biais identifiés et documentés

| Biais | Impact | Traitement |
|-------|--------|------------|
| Confusion Bénin-pays / Benin City (Nigeria) | Modéré | Documenté — non corrigeable par lat/lon |
| Centroïde générique (9.5°N, 2.25°E) pour 91% des events | Fort sur analyse géo | Zone "Non localisé" créée explicitement |
| Biais anglophone (49.5% des sources) | Modéré | Colonne `communaute_linguistique` |
| Data leakage CAMEO pour le ML | Critique | Variables exclues du Random Forest |

---

## Usage de l'Intelligence Artificielle

Conformément au règlement du hackathon, nous déclarons avoir utilisé
des outils d'intelligence artificielle (Claude — Anthropic) dans le cadre
de ce projet, principalement pour :

- La génération de suggestions de code revues, comprises et adaptées par l'équipe
- La structuration des analyses et la rédaction de documentation
- L'aide à la réflexion analytique et à l'interprétation des résultats

Chaque ligne de code produite a été comprise, testée et validée
par au moins un membre de l'équipe avant intégration.

---

## Equipe

| Membre | Rôle |
|--------|------|
| **AGONHOUN Bonaventure** | ML Engineer — Chef d'équipe |
| **KRE PAUL ROCHE ENOCK** | Data Analyst |
| **Alvaro ANTONIO** | ML Engineer |
| **HOUETO Jean-Vladimir** | Data Scientist |

---

## Hackathon

**iSHEERO × DataCamp Donates · Hackathon 2026**
Benin Insights Challenge · Groupe 16
Kickoff : 27 avril 2026 · Demo Day : 9 mai 2026

[isheero.com](https://isheero.com)
