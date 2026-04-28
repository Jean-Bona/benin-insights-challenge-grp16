Bénin Insights Challenge 2026 — Groupe 16

📌 Présentation du Projet

Ce projet est réalisé dans le cadre du Hackathon iSHEERO x DataCamp Donates. Notre objectif est d'analyser les données mondiales issues de la base GDELT (Global Database of Events, Language, and Tone) pour en extraire des insights pertinents sur le contexte béninois au cours des 12 derniers mois.

Le projet aboutira à la création d'un Dashboard interactif destiné à visualiser les dynamiques socio-politiques, les acteurs majeurs et l'évolution du ton médiatique concernant le Bénin.



📂 Architecture du Dépôt

.
├── dashboard/          # Application Streamlit (Interface finale)
├── data/               # Données GDELT (Dossier local - ignoré par Git)
│   ├── raw/            # Extractions brutes de BigQuery
│   └── processed/      # Données nettoyées pour le Dashboard/ML
├── models/             # Modèles de Machine Learning et évaluations
├── notebooks/          # Zone d'analyse exploratoire et de recherche
├── credentials/        # Dossier pour les clés JSON Google Cloud (ignoré)
├── environment.yml     # Configuration de l'environnement Conda
└── requirements.txt    # Dépendances Python (Pip)


🛠️ Installation et Configuration

Pour reproduire l'environnement de travail et lancer le projet, suivez ces étapes :

Clonage du dépôt :

git clone [https://github.com/votre-compte/benin-insights-challenge-grp16.git](https://github.com/votre-compte/benin-insights-challenge-grp16.git)
cd benin-insights-challenge-grp16


Mise en place de l'environnement (Conda) :

conda env create -f environment.yml
conda activate benin-insights


Configuration des accès (BigQuery) :

Placez votre fichier de clé JSON Google Cloud dans le dossier credentials/.

Créez un fichier .env à la racine pour y stocker votre GCP_PROJECT_ID.

🤖 Déclaration d'Usage de l'IA

Conformément au règlement du Hackathon, le Groupe 16 déclare utiliser des outils d'IA (Gemini 2.5) pour les tâches suivantes :

Structuration de la documentation technique et du dépôt.

Assistance au débogage de l'environnement de développement.

Optimisation de scripts de traitement de données.

L'intégralité des analyses, des interprétations et de la narration du projet est le produit exclusif de la réflexion de l'équipe.

📄 Licence

Ce projet est réalisé dans un cadre éducatif et compétitif pour le Hackathon 2026.