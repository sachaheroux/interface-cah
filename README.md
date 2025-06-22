# Interface CAH - Gestion de Construction

Une interface web interne pour la gestion d'une compagnie de construction qui bâtit et loue des immeubles résidentiels.

## 🏗️ Architecture du Projet

- **Backend**: FastAPI (Python) - API REST
- **Frontend**: React + Vite (JavaScript) - Interface utilisateur
- **Base de données**: À définir plus tard
- **Déploiement**: 
  - Backend sur Render
  - Frontend sur Vercel
  - Code source sur GitHub

## 📁 Structure du Projet

```
Interface CAH/
├── backend/          # API FastAPI
│   ├── app/
│   ├── requirements.txt
│   └── main.py
├── frontend/         # Application React
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── README.md
└── .gitignore
```

## 🚀 Démarrage Rapide

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

## 📋 Modules de l'Interface

1. **Tableau de bord** - Vue d'ensemble
2. **Immeubles** - Gestion des bâtiments
3. **Locataires** - Fiches locataires
4. **Entretien & Réparations** - Suivi des interventions
5. **Facturation & Dépenses** - Gestion financière
6. **Employés & Temps** - Feuilles de temps
7. **Sous-traitants** - Gestion fournisseurs
8. **Projets de Construction** - Suivi projets
9. **Documents** - Bibliothèque de fichiers
10. **Paramètres & Utilisateurs** - Administration

## 🔗 Communication Frontend ↔ Backend

Le frontend React communique avec l'API FastAPI via des requêtes HTTP REST.

## 📦 Déploiement

### GitHub → Render (Backend)
1. Push le code sur GitHub
2. Connecter le repo à Render
3. Render détecte automatiquement FastAPI et déploie

### GitHub → Vercel (Frontend)
1. Push le code sur GitHub
2. Connecter le repo à Vercel
3. Vercel détecte automatiquement Vite et déploie

## 👥 Types d'Utilisateurs

- **Administrateur**: Accès complet
- **Employés**: Accès limité (heures, tâches)
- **Contremaîtres/Gestionnaires**: Accès immeubles, travaux, employés
- **Sous-traitants**: Accès restreint aux bons de travail 